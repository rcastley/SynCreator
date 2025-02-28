import json
import os
import time

import requests  # type: ignore
from flask import (Blueprint, abort, g, jsonify, make_response, redirect, render_template, request, url_for)  # type: ignore
from werkzeug.exceptions import abort  # type: ignore

from flaskr.auth import login_required
from flaskr.db import get_db

books = [
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
        "published": "1973",
    },
    {
        "id": 2,
        "title": "Dhalgren",
        "author": "Samuel R. Delany",
        "first_sentence": "to wound the autumnal city.",
        "published": "1975",
    },
]

bp = Blueprint("scc", __name__)


@bp.route("/")
def index():
    if g.user is None:
        return redirect(url_for("auth.login"))
    else:
        db = get_db()
        condition = db.execute(
            "SELECT condition" " FROM scc WHERE username = ?", (g.user["username"],)
        ).fetchone()
        return render_template("scc/index.html", condition=condition)


@bp.route("/rum/", methods=("GET", "POST"))
def rum():
    if g.user is None:
        return redirect(url_for("auth.login"))
    else:
        if request.method == "POST":
            realm = request.form["realm"]
            ingesttoken = request.form["ingesttoken"]
            rumtoken = request.form["rumtoken"]

        db = get_db()
        db.execute(
            "UPDATE scc" " SET realm = ?, rum_token = ?, ingest_token = ? WHERE username = ?",
            (realm, rumtoken, ingesttoken, g.user["username"]),
        )
        db.commit()
        return redirect(url_for("index"))


@bp.route("/splunk/", methods=("GET", "POST"))
def splunk():
    if g.user is None:
        return redirect(url_for("auth.login"))
    else:
        if request.method == "POST":
            hec_url = request.form["hec_url"]
            hec_token = request.form["hec_token"]

        db = get_db()
        db.execute(
            "UPDATE scc" " SET hec_url = ?, hec_token = ? WHERE username = ?",
            (hec_url, hec_token, g.user["username"]),
        )
        db.commit()
        return redirect(url_for("index"))


@bp.route("/set/<string:condition>", methods=("GET", "POST"))
def set(condition):
    if g.user is None:
        return redirect(url_for("auth.login"))
    else:
        if g.user["ingest_token"] is not None:
            data = [{
                "category": "USER_DEFINED",
                "eventType": "condition_changed",
                "dimensions": {
                    "condition": condition,
                    "source": "syncreator",
                    "user": g.user["username"]
                    }
            }]
            requests.post(
                f"https://ingest.{g.user['realm']}.signalfx.com/v2/event",
                headers={"X-SF-TOKEN": g.user["ingest_token"]},
                json=data,
            )
        db = get_db()
        db.execute(
            "UPDATE scc" " SET condition = ? WHERE username = ?",
            (condition, g.user["username"]),
        )
        db.commit()
        return redirect(url_for("index"))


@bp.route("/view/<string:username>")
def view(username):
    db = get_db()
    settings = db.execute(
        "SELECT condition, realm, rum_token, ingest_token, username as u"
        " FROM scc WHERE username = ?",
        (username,),
    ).fetchone()
    
    if settings is not None:

        if settings[0] == "404error":
            resp = render_template("scc/" + settings[0] + ".html", settings=settings)
            return (resp, 404)
        elif settings[0] == "500error":
            resp = render_template("scc/" + settings[0] + ".html", settings=settings)
            return (resp, 500)
        elif settings[0] == "timeout":
            time.sleep(62)
            return render_template("scc/" + settings[0] + ".html", settings=settings)
        elif settings[0] == "cookies":
            resp = make_response(
                render_template("scc/" + settings[0] + ".html", settings=settings)
            )
            resp.set_cookie("SplunkSynthetic", "abc123")
            return resp
        else:
            return render_template("scc/" + settings[0] + ".html", settings=settings)
    else:
        return render_template("scc/404error.html", settings=settings)

@bp.route("/view/<string:username>/product/<string:productid>")
def product(username, productid):
    db = get_db()
    settings = db.execute(
        "SELECT condition, realm, rum_token, ingest_token, username as u"
        " FROM scc WHERE username = ?",
        (username,),
    ).fetchone()
    return render_template("product/" + productid + "", settings=settings)


@bp.route("/view/<string:username>/cart")
def cart(username):
    db = get_db()
    settings = db.execute(
        "SELECT condition, realm, rum_token, ingest_token, username as u"
        " FROM scc WHERE username = ?",
        (username,),
    ).fetchone()
    return render_template("cart/index.html", settings=settings)


@bp.route("/view/<string:username>/cart/checkout")
def checkout(username):
    db = get_db()
    settings = db.execute(
        "SELECT condition, realm, rum_token, ingest_token, username as u"
        " FROM scc WHERE username = ?",
        (username,),
    ).fetchone()
    return render_template("cart/checkout/index.html", settings=settings)


@bp.route("/air-plant")
def airplant():
    return render_template("scc/air-plant.html")


@bp.route("/api/v1/<string:username>/books/all", methods=["GET"])
def api_all(username):
    return jsonify(books)


@bp.route("/api/v1/<string:username>/books", methods=["GET"])
def api_id(username):
    # Check if an ID was provided as part of the URL.
    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "Error: No id field provided. Please specify an id."

    results = []

    for book in books:
        if book["id"] == id:
            results.append(book)

    if len(results) == 0:
        abort(404)

    return jsonify(results)


@bp.route("/api/v1/<string:username>/books", methods=["POST"])
def create_task(username):
    if not request.json or not "title" in request.json:
        abort(400)
    book = {
        "id": books[-1]["id"] + 1,
        "title": request.json["title"],
        "author": request.json.get("author", "Not set"),
        "first_sentence": request.json.get("first_sentence", "Not set"),
        "year_published": request.json.get("year_published", "Not set"),
    }
    return jsonify({"book": book}), 201


@bp.route("/create_browser_test")
def create_browser_test():
    if g.user is None:
        return redirect(url_for("auth.login"))
    else:
        document_path = os.path.dirname(os.path.abspath(__file__)) + "/synthetic_tests/homepage-us.json"
        
        with open(document_path, "r") as f:
            data = json.load(f)
            data['test']['name'] = f"[syncreator - {g.user['username']}] Home - Desktop {g.user['realm']}"
            data['test']['transactions'][0]['steps'][0]['url'] = "https://splunko11y.com/syncreator/view/" + g.user["username"]
            data['test']['transactions'][0]['steps'][0]['options']['url'] = "https://splunko11y.com/syncreator/view/" + g.user["username"]

        response = requests.post(f"https://api.{g.user['realm']}.signalfx.com/v2/synthetics/tests/browser",
                                 headers={"X-SF-TOKEN": g.user["ingest_token"]},
                                 json=data
                                 )

        if not response.ok:
            return f"Error: **{response.status_code}** {response.reason}"
        else:
            return redirect(url_for("index"))

@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)
