
import os
import importlib

from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.translations import get_translations

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

SUPPORTED_LANGUAGES = ("en", "te", "ta", "hi")


def create_app(config_class):
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(root, "templates"),
        static_folder=os.path.join(root, "static"),
    )

    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database and login manager
    db.init_app(app)
    login_manager.init_app(app)

    # Remember the selected language
    @app.before_request
    def remember_language():
        selected_language = request.args.get("lang")

        if selected_language in SUPPORTED_LANGUAGES:
            session["language"] = selected_language

    # Make translations available in every template
    @app.context_processor
    def inject_language():
        language = session.get("language", "en")

        if language not in SUPPORTED_LANGUAGES:
            language = "en"

        return {
            "current_language": language,
            "supported_languages": SUPPORTED_LANGUAGES,
            "t": get_translations(language),
        }

    # Import database models
    from app.models import user, field, analysis  # noqa: F401
    from app.models.user import User

    # Load logged-in user
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    # Register existing application routes
    route_names = (
        "auth",
        "dashboard",
        "analysis",
        "history",
        "export",
        "weed_management",
    )

    for name in route_names:
        module = importlib.import_module(
            f"app.routes.{name}"
        )
        app.register_blueprint(module.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
