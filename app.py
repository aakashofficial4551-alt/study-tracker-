from flask import Flask, redirect, url_for
import os

from config import Config
from extensions import db, bcrypt, login_manager, migrate

# Import models
import models

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.subject import subject_bp
from routes.chapter import chapter_bp
from routes.study import study_bp
from routes.calendar import calendar_bp
from routes.analytics import analytics_bp
from routes.settings import settings_bp
from routes.task import task_bp


def create_app():
    app = Flask(__name__)

    # Load Config
    app.config.from_object(Config)

    # Create instance folder
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(chapter_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(task_bp)

    # Create Database
    with app.app_context():
        db.create_all()

    return app


app = create_app()


@app.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))


if __name__ == "__main__":
    app.run(debug=True)