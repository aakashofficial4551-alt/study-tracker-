from datetime import datetime, timedelta
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.user import User
from models.settings import DeviceLocation
from models.rest import LiveDevice
from models.habits import DailyProgress
from models.study_session import StudySession
from models.gym import GymLog
from models.mock_test import TestRecord

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Apna admin username yahan set rakho (ye user login karte hi /admin/ access kar payega)
ADMIN_USERNAMES = {"bikash", "admin", "urrecords"}


def is_admin_user():
    if not current_user.is_authenticated:
        return False
    uname = (current_user.username or "").strip().lower()
    return uname in ADMIN_USERNAMES or current_user.id == 1


@admin_bp.route("/")
@login_required
def index():
    if not is_admin_user():
        abort(404)

    users = User.query.order_by(User.id.asc()).all()
    locations = {loc.user_id: loc for loc in DeviceLocation.query.all()}
    live_devs = LiveDevice.query.order_by(LiveDevice.updated_at.desc()).all()

    user_cards = []
    for u in users:
        loc = locations.get(u.id)
        dev = next((d for d in live_devs if d.user_id == u.id), None)

        lat = dev.latitude if (dev and dev.latitude is not None) else (loc.latitude if loc else None)
        lng = dev.longitude if (dev and dev.longitude is not None) else (loc.longitude if loc else None)
        acc = dev.accuracy if (dev and dev.accuracy is not None) else (loc.accuracy if loc else None)
        updated = dev.updated_at if (dev and dev.updated_at) else (loc.updated_at if loc else None)
        address = (dev.address if (dev and dev.address) else (loc.address if loc else "")) or ""

        # Check if pinged in last 2 minutes
        now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
        is_online = bool(updated and (now_ist - updated) <= timedelta(minutes=2))

        study_secs = sum((s.duration or 0) for s in StudySession.query.filter_by(user_id=u.id).all())
        task_days = DailyProgress.query.filter_by(user_id=u.id).count()
        gym_days = GymLog.query.filter_by(user_id=u.id).count()
        tests_count = TestRecord.query.filter_by(user_id=u.id).count()

        user_cards.append({
            "user": u,
            "lat": lat,
            "lng": lng,
            "acc": acc,
            "address": address,
            "updated": updated.strftime("%d %b %Y, %I:%M %p") if updated else "No GPS yet",
            "is_online": is_online,
            "study_mins": study_secs // 60,
            "task_days": task_days,
            "gym_days": gym_days,
            "tests_count": tests_count,
        })

    return render_template("admin/index.html", user_cards=user_cards)
