import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Get database connection, creating it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database schema."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def ensure_db_exists():
    """Create database if it doesn't exist. Called on app startup."""
    db_path = current_app.config["DATABASE"]

    # Create instance directory if needed
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Initialize if database doesn't exist
    if not os.path.exists(db_path):
        init_db()
        current_app.logger.info(f"Database initialized at {db_path}")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Database initialized.")


def init_app(app):
    """Register database functions with Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # Auto-initialize database on first request
    with app.app_context():
        ensure_db_exists()
