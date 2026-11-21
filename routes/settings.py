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

from extensions import db
from models.settings import DeviceLocation

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)

# Kept hidden for now; ready to enable Friends & Messaging in the future
ENABLE_MESSAGING = False


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


@settings_bp.route("/")
@login_required
def index():
    saved_loc = DeviceLocation.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "settings/index.html",
        saved_loc=saved_loc,
        enable_messaging=ENABLE_MESSAGING,
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
