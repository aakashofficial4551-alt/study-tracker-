from flask import Flask, Response, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user
from sqlalchemy import inspect, text
import os
import struct
import zlib

from config import Config
from extensions import db, bcrypt, login_manager, migrate

# Import models
import models
from models.user import User
from models.habits import DailyProgress
from models.gym import GymLog
from models.mock_test import TestRecord
from models.topic import SyllabusChapter, seed_cbse_syllabus
from models.settings import DeviceLocation
from models.rest import RestMessage, LiveDevice

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.subject import subject_bp
from routes.chapter import chapter_bp
from routes.study import study_bp
from routes.analytics import analytics_bp
from routes.task import task_bp
from routes.habits import habits_bp
from routes.gym import gym_bp
from routes.settings import settings_bp
from routes.rest import rest_bp

_ICON_CACHE = {}


def build_ur_icon_png(size):
    """Generates a valid PNG icon (UR RECORDS theme) if static icon file is missing."""
    if size in _ICON_CACHE:
        return _ICON_CACHE[size]

    bg = bytes((6, 6, 9))
    card = bytes((17, 17, 24))
    pink = bytes((255, 46, 136))
    red = bytes((255, 36, 66))
    white = bytes((248, 250, 252))

    pad = size // 12
    bw = max(4, size // 32)
    inner_min = pad + bw
    inner_max = size - pad - bw
    outer_max = size - pad
    bar_y0 = int(size * 0.74)
    bar_y1 = int(size * 0.79)
    bar_x0 = int(size * 0.24)
    bar_x1 = int(size * 0.76)

    def in_ur(nx, ny):
        # Letter U
        if 20 <= nx <= 46 and 30 <= ny <= 68:
            if nx <= 27 or nx >= 39 or ny >= 61:
                return True
        # Letter R
        if 54 <= nx <= 80 and 30 <= ny <= 68:
            if nx <= 61:
                return True
            if (30 <= ny <= 37 or 47 <= ny <= 53) and nx <= 75:
                return True
            if 73 <= nx <= 80 and 33 <= ny <= 50:
                return True
            if ny >= 53:
                diag_x = 63 + (ny - 53) * 0.9
                if diag_x - 3.5 <= nx <= diag_x + 4.5:
                    return True
        return False

    grid = [[in_ur(gx, gy) for gx in range(100)] for gy in range(100)]
    rows = []

    for y in range(size):
        gy = (y * 100) // size
        if y < pad or y >= outer_max:
            row = b"\x00" + bg * size
        elif y < inner_min or y >= inner_max:
            row = b"\x00" + bg * pad + pink * (size - 2 * pad) + bg * pad
        else:
            line = bytearray(1 + size * 3)
            line[1:1 + pad * 3] = bg * pad
            line[1 + pad * 3:1 + inner_min * 3] = pink * bw
            line[1 + inner_min * 3:1 + inner_max * 3] = card * (inner_max - inner_min)
            line[1 + inner_max * 3:1 + outer_max * 3] = pink * bw
            line[1 + outer_max * 3:] = bg * pad

            if bar_y0 <= y < bar_y1:
                line[1 + bar_x0 * 3:1 + bar_x1 * 3] = red * (bar_x1 - bar_x0)
            elif 28 <= gy <= 70:
                g_row = grid[gy]
                for x in range(int(size * 0.18), int(size * 0.82)):
                    if g_row[(x * 100) // size]:
                        idx = 1 + x * 3
                        line[idx:idx + 3] = white
            row = bytes(line)
        rows.append(row)

    raw = b"".join(rows)

    def png_chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw, 6))
        + png_chunk(b"IEND", b"")
    )
    _ICON_CACHE[size] = png_bytes
    return png_bytes


def ensure_schema_columns():
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

    app.config.from_object(Config)
    app.config["DISABLE_AUTH"] = True

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def home():
        return redirect(url_for("dashboard.dashboard"))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(chapter_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(gym_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(rest_bp)

    @app.before_request
    def auto_login_owner():
        if not app.config.get("DISABLE_AUTH"):
            return
        if request.endpoint in (
            "static",
            "manifest",
            "service_worker",
            "favicon",
            "icon_192",
            "icon_512",
        ):
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

    with app.app_context():
        db.create_all()
        ensure_schema_columns()
        seed_cbse_syllabus()

    return app


app = create_app()


def serve_app_icon(size):
    filename = f"icon-{size}.png"
    for folder in (os.path.join(app.static_folder, "icons"), app.static_folder):
        if os.path.exists(os.path.join(folder, filename)):
            return send_from_directory(folder, filename, mimetype="image/png")

    resp = Response(build_ur_icon_png(size), mimetype="image/png")
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp


@app.route("/icon-192.png")
def icon_192():
    return serve_app_icon(192)


@app.route("/icon-512.png")
def icon_512():
    return serve_app_icon(512)


@app.route("/favicon.ico")
def favicon():
    return serve_app_icon(192)


@app.route("/manifest.json")
def manifest():
    return send_from_directory(
        app.static_folder,
        "manifest.json",
        mimetype="application/manifest+json",
    )


@app.route("/sw.js")
def service_worker():
    response = send_from_directory(
        app.static_folder,
        "sw.js",
        mimetype="application/javascript",
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Service-Worker-Allowed"] = "/"
    return response


if __name__ == "__main__":
    app.run(debug=True)
