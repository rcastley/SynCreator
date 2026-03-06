import os

from flask import Flask


def create_app(test_config=None):
    """Application factory for the SynCreator Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-in-production"),
        DATABASE=os.path.join(app.instance_path, "scc.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import scc
    app.register_blueprint(scc.bp)
    app.add_url_rule("/", endpoint="index")

    return app
