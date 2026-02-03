"""
SynCreator - Main application routes and business logic.

This module handles condition management, Splunk integrations,
and the public-facing synthetic test endpoints.
"""
import json
import os
import time

import requests
from flask import Blueprint, flash, g, jsonify, make_response, redirect, render_template, request, url_for

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("scc", __name__)

# Valid conditions - single source of truth
VALID_CONDITIONS = {
    "default", "404error", "500error", "502error", "503error", "429ratelimit",
    "validationerror", "contenterror", "largeimage", "heroimage",
    "contentdelay", "slowttfb", "timeout", "cookies", "missingcss", "missingjs",
    "redirectloop", "maintenance", "brokenlinks", "uncaughtexception", "layoutshift",
    "security-jsinjected", "security-eskimmer", "security-deface", "security-crypto"
}

# Mock book data for API testing
BOOKS = [
    {
        "id": 0,
        "title": "A Fire Upon the Deep",
        "author": "Vernor Vinge",
        "first_sentence": "The coldsleep itself was dreamless.",
        "year_published": "1992",
    },
    {
        "id": 1,
        "title": "The Ones Who Walk Away From Omelas",
        "author": "Ursula K. Le Guin",
        "first_sentence": "With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.",
        "year_published": "1973",
    },
    {
        "id": 2,
        "title": "Dhalgren",
        "author": "Samuel R. Delany",
        "first_sentence": "to wound the autumnal city.",
        "year_published": "1975",
    },
]

# Timeout for external API calls (seconds)
API_TIMEOUT = 5


def get_user_settings(username):
    """Fetch user settings by username.

    Returns:
        sqlite3.Row or None: User settings if found, None otherwise.
    """
    return get_db().execute(
        "SELECT condition, realm, rum_token, ingest_token, username as u "
        "FROM scc WHERE username = ?",
        (username,),
    ).fetchone()


def send_condition_event(user, condition):
    """Send condition change event to Splunk Observability Cloud and/or Splunk Enterprise.

    This is fire-and-forget - failures don't affect the user action.
    """
    # Send to Observability Cloud
    if user["ingest_token"] and user["realm"]:
        data = [{
            "category": "USER_DEFINED",
            "eventType": "condition_changed",
            "dimensions": {
                "condition": condition,
                "source": "syncreator",
                "user": user["username"]
            }
        }]
        try:
            requests.post(
                f"https://ingest.{user['realm']}.signalfx.com/v2/event",
                headers={"X-SF-TOKEN": user["ingest_token"]},
                json=data,
                timeout=API_TIMEOUT,
            )
        except Exception:
            pass  # Fire-and-forget: don't let external API failures affect user

    # Send to Splunk Enterprise via HEC
    if user["hec_url"] and user["hec_token"]:
        event = {
            "event": {
                "condition": condition,
                "user": user["username"],
                "source": "syncreator"
            },
            "sourcetype": "syncreator:condition_change",
            "source": "syncreator"
        }
        try:
            requests.post(
                user["hec_url"],
                headers={"Authorization": f"Splunk {user['hec_token']}"},
                json=event,
                timeout=API_TIMEOUT,
                verify=True,
            )
        except Exception:
            pass  # Fire-and-forget: don't let external API failures affect user


# =============================================================================
# Dashboard Routes (Authenticated)
# =============================================================================

@bp.route("/")
@login_required
def index():
    """Main dashboard showing current condition and available conditions."""
    condition = get_db().execute(
        "SELECT condition FROM scc WHERE username = ?",
        (g.user["username"],)
    ).fetchone()
    return render_template("scc/index.html", condition=condition)


@bp.route("/rum/", methods=["POST"])
@login_required
def rum():
    """Update Observability Cloud configuration (realm, tokens)."""
    realm = request.form.get("realm", "").strip()
    ingesttoken = request.form.get("ingesttoken", "").strip()
    rumtoken = request.form.get("rumtoken", "").strip()

    db = get_db()
    db.execute(
        "UPDATE scc SET realm = ?, rum_token = ?, ingest_token = ? WHERE username = ?",
        (realm or None, rumtoken or None, ingesttoken or None, g.user["username"]),
    )
    db.commit()
    flash("Observability Cloud configuration saved.", "success")
    return redirect(url_for("index"))


@bp.route("/splunk/", methods=["POST"])
@login_required
def splunk():
    """Update Splunk Enterprise HEC configuration."""
    hec_url = request.form.get("hec_url", "").strip()
    hec_token = request.form.get("hec_token", "").strip()

    db = get_db()
    db.execute(
        "UPDATE scc SET hec_url = ?, hec_token = ? WHERE username = ?",
        (hec_url or None, hec_token or None, g.user["username"]),
    )
    db.commit()
    flash("Splunk Enterprise configuration saved.", "success")
    return redirect(url_for("index"))


@bp.route("/set/<string:condition>")
@login_required
def set_condition(condition):
    """Change the active condition for the current user."""
    if condition not in VALID_CONDITIONS:
        flash(f"Invalid condition: {condition}", "error")
        return redirect(url_for("index"))

    send_condition_event(g.user, condition)

    db = get_db()
    db.execute(
        "UPDATE scc SET condition = ? WHERE username = ?",
        (condition, g.user["username"]),
    )
    db.commit()

    # HTMX request - return partial template
    if request.headers.get("HX-Request"):
        new_condition = db.execute(
            "SELECT condition FROM scc WHERE username = ?",
            (g.user["username"],)
        ).fetchone()
        return render_template("scc/_cards.html", condition=new_condition)

    return redirect(url_for("index"))


@bp.route("/create_browser_test")
@login_required
def create_browser_test():
    """Deploy a Splunk Synthetics browser test for this user's endpoint."""
    if not g.user["realm"] or not g.user["ingest_token"]:
        flash("Please configure Observability Cloud (realm and ingest token) before deploying a test.", "error")
        return redirect(url_for("index"))

    try:
        document_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "synthetic_tests",
            "homepage-us.json"
        )

        with open(document_path, "r") as f:
            data = json.load(f)
            data["test"]["name"] = f"[syncreator - {g.user['username']}] Home - Desktop {g.user['realm']}"
            test_url = f"https://splunko11y.com/syncreator/view/{g.user['username']}"
            data["test"]["transactions"][0]["steps"][0]["url"] = test_url
            data["test"]["transactions"][0]["steps"][0]["options"]["url"] = test_url

        response = requests.post(
            f"https://api.{g.user['realm']}.signalfx.com/v2/synthetics/tests/browser",
            headers={"X-SF-TOKEN": g.user["ingest_token"]},
            json=data,
            timeout=API_TIMEOUT,
        )

        if not response.ok:
            flash(f"Failed to create test: {response.status_code} {response.reason}", "error")
        else:
            flash("Synthetics test deployed successfully!", "success")

    except requests.RequestException as e:
        flash(f"Network error creating test: {e}", "error")
    except Exception as e:
        flash(f"Error creating test: {e}", "error")

    return redirect(url_for("index"))


# =============================================================================
# Public View Routes (No Authentication)
# =============================================================================

@bp.route("/view/<string:username>")
def view(username):
    """Public view of a user's current condition - used by synthetic tests."""
    settings = get_user_settings(username)

    if settings is None:
        return render_template("scc/404error.html", settings=None), 404

    condition = settings["condition"]
    if condition not in VALID_CONDITIONS:
        condition = "default"

    # Handle special conditions
    if condition == "404error":
        return render_template("scc/404error.html", settings=settings), 404

    if condition == "500error":
        return render_template("scc/500error.html", settings=settings), 500

    if condition == "502error":
        return render_template("scc/502error.html", settings=settings), 502

    if condition == "503error":
        return render_template("scc/503error.html", settings=settings), 503

    if condition == "429ratelimit":
        resp = make_response(render_template("scc/429ratelimit.html", settings=settings))
        resp.headers["Retry-After"] = "60"
        return resp, 429

    if condition == "slowttfb":
        time.sleep(3)  # 3 second delay before first byte
        return render_template("scc/default.html", settings=settings)

    if condition == "redirectloop":
        # Redirect to self, creating an infinite loop
        return redirect(request.url)

    if condition == "maintenance":
        return render_template("scc/maintenance.html", settings=settings), 503

    if condition == "timeout":
        time.sleep(62)
        return render_template("scc/timeout.html", settings=settings)

    if condition == "cookies":
        resp = make_response(render_template("scc/cookie.html", settings=settings))
        resp.set_cookie("SplunkSynthetic", "abc123")
        return resp

    return render_template(f"scc/{condition}.html", settings=settings)


@bp.route("/view/<string:username>/product/<string:productid>")
def product(username, productid):
    """Product detail page for the mock store."""
    settings = get_user_settings(username)
    if settings is None:
        return render_template("scc/404error.html", settings=None), 404
    return render_template(f"product/{productid}", settings=settings)


@bp.route("/view/<string:username>/cart")
def cart(username):
    """Shopping cart page for the mock store."""
    settings = get_user_settings(username)
    if settings is None:
        return render_template("scc/404error.html", settings=None), 404
    return render_template("cart/index.html", settings=settings)


@bp.route("/view/<string:username>/cart/checkout")
def checkout(username):
    """Checkout page for the mock store."""
    settings = get_user_settings(username)
    if settings is None:
        return render_template("scc/404error.html", settings=None), 404
    return render_template("cart/checkout/index.html", settings=settings)


@bp.route("/air-plant")
def airplant():
    """Air plant detail page - used for AJAX content loading tests."""
    return render_template("scc/air-plant.html")


# =============================================================================
# Mock API Routes (No Authentication)
# These endpoints exist purely for API synthetic testing.
# Data is not persisted - resets on application restart.
# =============================================================================

@bp.route("/api/v1/<string:username>/books/all", methods=["GET"])
def api_all(username):
    """Return all books in the mock collection."""
    # username is part of the URL for namespacing but not used
    return jsonify(BOOKS)


@bp.route("/api/v1/<string:username>/books", methods=["GET"])
def api_get_book(username):
    """Return a specific book by ID query parameter."""
    if "id" not in request.args:
        return jsonify({"error": "No id field provided. Please specify an id."}), 400

    try:
        book_id = int(request.args["id"])
    except ValueError:
        return jsonify({"error": "Invalid id format. Must be an integer."}), 400

    results = [book for book in BOOKS if book["id"] == book_id]

    if not results:
        return jsonify({"error": "Book not found."}), 404

    return jsonify(results)


@bp.route("/api/v1/<string:username>/books", methods=["POST"])
def api_create_book(username):
    """Mock endpoint for creating a book.

    NOTE: This is a mock endpoint for API testing. Created books are NOT
    persisted and will not appear in subsequent GET requests.
    """
    if not request.json or "title" not in request.json:
        return jsonify({"error": "Request must include JSON with 'title' field."}), 400

    book = {
        "id": BOOKS[-1]["id"] + 1 if BOOKS else 0,
        "title": request.json["title"],
        "author": request.json.get("author", "Unknown"),
        "first_sentence": request.json.get("first_sentence", ""),
        "year_published": request.json.get("year_published", "Unknown"),
    }
    return jsonify({"book": book, "note": "This is a mock endpoint. Book was not persisted."}), 201


@bp.errorhandler(404)
def not_found(_error):
    """Handle 404 errors for API routes."""
    return jsonify({"error": "Not found"}), 404
