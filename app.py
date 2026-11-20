from flask import Flask, redirect, url_for, request
from flask_login import current_user, login_user
from sqlalchemy import inspect, text
import os

from config import Config
from extensions import db, bcrypt, login_manager, migrate

# Import models
import models
from models.user import User
from models.habits import DailyProgress
from models.gym import GymLog
from models.mock_test import TestRecord

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.subject import subject_bp
from routes.chapter import chapter_bp
from routes.study import study_bp
from routes.analytics import analytics_bp
from routes.settings import settings_bp
from routes.task import task_bp
from routes.habits import habits_bp
from routes.gym import gym_bp
# from routes.calendar import calendar_bp  # Future mein wapas on kar sakte ho


def ensure_schema_columns():
    """Purane SQLite DB mein naye columns safely add karta hai taaki error na aaye."""
    inspector = inspect(db.engine)
    if "daily_progress" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("daily_progress")}
        if "learn_new" not in cols:
            db.session.execute(
                text("ALTER TABLE daily_progress ADD COLUMN learn_new BOOLEAN DEFAULT 0")
            )
        if "meditation" not in cols:
            db.session.execute(
                text("ALTER TABLE daily_progress ADD COLUMN meditation BOOLEAN DEFAULT 0")
            )
        db.session.commit()


def create_app():
    app = Flask(__name__)

    # Load Config
    app.config.from_object(Config)

    # Login abhi OFF hai — future mein login wapas lane ke liye bas False kar dena
    app.config["DISABLE_AUTH"] = True

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
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(gym_bp)
    # app.register_blueprint(calendar_bp)  # Disabled for now

    # Temporary auto-login while DISABLE_AUTH is True
    @app.before_request
    def auto_login_owner():
        if not app.config.get("DISABLE_AUTH"):
            return
        if request.endpoint == "static":
            return
        if not current_user.is_authenticated:
            user = User.query.first()
            if not user:
                hashed = bcrypt.generate_password_hash("studyos123").decode("utf-8")
                user = User(
                    full_name="Champion",
                    username="studyos_user",
                    email="owner@studyos.local",
                    password=hashed,
                )
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=True)

    # Create / Upgrade Database Tables
    with app.app_context():
        db.create_all()
        ensure_schema_columns()

    return app


app = create_app()


@app.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
