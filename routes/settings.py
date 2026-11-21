from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user, logout_user
from sqlalchemy import or_

from extensions import db
from models.user import User
from models.habits import DailyProgress
from models.gym import GymLog
from models.study_session import StudySession
from models.mock_test import TestRecord
from models.settings import DeviceLocation
from models.rest import RestMessage, LiveDevice

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


@settings_bp.route("/")
@login_required
def index():
    saved_loc = DeviceLocation.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "settings/index.html",
        saved_loc=saved_loc,
        auth_disabled=current_app.config.get("DISABLE_AUTH", False),
    )


@settings_bp.route("/location", methods=["POST"])
@login_required
def save_location():
    data = request.get_json(silent=True) or {}
    try:
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
        accuracy = float(data.get("accuracy") or 0)
    except (TypeError, ValueError):
        return jsonify({"ok": False}), 400

    address = (data.get("address") or "").strip()[:300]
    now_ist = get_ist_now()

    loc = DeviceLocation.query.filter_by(user_id=current_user.id).first()
    if not loc:
        loc = DeviceLocation(user_id=current_user.id)
        db.session.add(loc)

    loc.latitude = lat
    loc.longitude = lng
    loc.accuracy = round(accuracy, 1)
    if address:
        loc.address = address
    loc.updated_at = now_ist

    db.session.commit()

    return jsonify({
        "ok": True,
        "updated_at": now_ist.strftime("%d %b %Y, %I:%M %p"),
    })


@settings_bp.route("/logout")
@login_required
def logout_action():
    if current_app.config.get("DISABLE_AUTH"):
        flash("Account login is currently disabled.", "info")
        return redirect(url_for("settings.index"))

    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    uid = current_user.id

    DailyProgress.query.filter_by(user_id=uid).delete()
    GymLog.query.filter_by(user_id=uid).delete()
    StudySession.query.filter_by(user_id=uid).delete()
    TestRecord.query.filter_by(user_id=uid).delete()
    DeviceLocation.query.filter_by(user_id=uid).delete()
    LiveDevice.query.filter_by(user_id=uid).delete()
    RestMessage.query.filter(
        or_(RestMessage.sender_id == uid, RestMessage.receiver_id == uid)
    ).delete(synchronize_session=False)

    try:
        from models.task import Task
        Task.query.filter_by(user_id=uid).delete()
    except Exception:
        pass

    user = User.query.get(uid)
    logout_user()
    if user:
        db.session.delete(user)
    db.session.commit()

    flash("Account and all data permanently deleted.", "info")
    if current_app.config.get("DISABLE_AUTH"):
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.register"))
