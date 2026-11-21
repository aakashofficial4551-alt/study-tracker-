from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from extensions import db
from models.user import User
from models.settings import DeviceLocation
from models.rest import RestMessage, LiveDevice

rest_bp = Blueprint(
    "rest",
    __name__,
    url_prefix="/rest"
)

ONLINE_WINDOW_MINUTES = 2


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


@rest_bp.route("/")
@login_required
def index():
    auth_disabled = bool(current_app.config.get("DISABLE_AUTH", False))
    target_user = None

    if not auth_disabled:
        target_id = request.args.get("u", type=int)
        if target_id and target_id != current_user.id:
            target_user = User.query.get(target_id)

    return render_template(
        "rest/index.html",
        auth_disabled=auth_disabled,
        target_user=target_user,
    )


@rest_bp.route("/search")
@login_required
def search_users():
    if current_app.config.get("DISABLE_AUTH", False):
        return jsonify({"users": []})

    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"users": []})

    matches = (
        User.query
        .filter(
            User.id != current_user.id,
            User.username.ilike(f"%{q}%")
        )
        .order_by(User.username.asc())
        .limit(15)
        .all()
    )

    return jsonify({
        "users": [
            {"id": u.id, "username": u.username, "full_name": u.full_name or u.username}
            for u in matches
        ]
    })


@rest_bp.route("/check")
@login_required
def check_latest():
    auth_disabled = bool(current_app.config.get("DISABLE_AUTH", False))
    device_id = (request.args.get("device_id") or "").strip()[:64]

    if auth_disabled:
        q = RestMessage.query.filter(RestMessage.receiver_id.is_(None))
        if device_id:
            q = q.filter(RestMessage.sender_device != device_id)
        latest = q.order_by(RestMessage.id.desc()).first()
    else:
        latest = (
            RestMessage.query
            .filter(RestMessage.receiver_id == current_user.id)
            .order_by(RestMessage.id.desc())
            .first()
        )

    return jsonify({"latest_id": latest.id if latest else 0})


@rest_bp.route("/feed")
@login_required
def feed():
    auth_disabled = bool(current_app.config.get("DISABLE_AUTH", False))
    device_id = (request.args.get("device_id") or "").strip()[:64]
    target_id = request.args.get("u", type=int)
    cutoff = get_ist_now() - timedelta(minutes=ONLINE_WINDOW_MINUTES)

    if auth_disabled:
        msgs = (
            RestMessage.query
            .filter(RestMessage.receiver_id.is_(None))
            .order_by(RestMessage.id.asc())
            .limit(100)
            .all()
        )
        items = [
            {
                "id": m.id,
                "body": m.body,
                "mine": bool(device_id and m.sender_device == device_id),
                "time": m.created_at.strftime("%I:%M %p") if m.created_at else "",
            }
            for m in msgs
        ]

        # Only return OTHER person's live location if online (never own location)
        peer_dev = None
        if device_id:
            peer_dev = (
                LiveDevice.query
                .filter(
                    LiveDevice.device_id != device_id,
                    LiveDevice.latitude.isnot(None),
                    LiveDevice.longitude.isnot(None),
                    LiveDevice.updated_at >= cutoff,
                )
                .order_by(LiveDevice.updated_at.desc())
                .first()
            )

        peer_location = None
        if peer_dev:
            peer_location = {
                "latitude": peer_dev.latitude,
                "longitude": peer_dev.longitude,
                "accuracy": peer_dev.accuracy,
                "updated_at": peer_dev.updated_at.strftime("%I:%M %p") if peer_dev.updated_at else "",
            }

        return jsonify({
            "items": items,
            "peer_online": peer_location is not None,
            "peer_location": peer_location,
        })

    # Authenticated 1-on-1 mode
    if not target_id or target_id == current_user.id:
        return jsonify({"items": [], "peer_online": False, "peer_location": None})

    msgs = (
        RestMessage.query
        .filter(
            or_(
                and_(RestMessage.sender_id == current_user.id, RestMessage.receiver_id == target_id),
                and_(RestMessage.sender_id == target_id, RestMessage.receiver_id == current_user.id),
            )
        )
        .order_by(RestMessage.id.asc())
        .limit(100)
        .all()
    )

    items = [
        {
            "id": m.id,
            "body": m.body,
            "mine": m.sender_id == current_user.id,
            "time": m.created_at.strftime("%I:%M %p") if m.created_at else "",
        }
        for m in msgs
    ]

    peer_loc = (
        DeviceLocation.query
        .filter(
            DeviceLocation.user_id == target_id,
            DeviceLocation.latitude.isnot(None),
            DeviceLocation.longitude.isnot(None),
            DeviceLocation.updated_at >= cutoff,
        )
        .first()
    )

    peer_location = None
    if peer_loc:
        peer_location = {
            "latitude": peer_loc.latitude,
            "longitude": peer_loc.longitude,
            "accuracy": peer_loc.accuracy,
            "updated_at": peer_loc.updated_at.strftime("%I:%M %p") if peer_loc.updated_at else "",
        }

    return jsonify({
        "items": items,
        "peer_online": peer_location is not None,
        "peer_location": peer_location,
    })


@rest_bp.route("/send", methods=["POST"])
@login_required
def send():
    auth_disabled = bool(current_app.config.get("DISABLE_AUTH", False))
    data = request.get_json(silent=True) or {}

    body = (data.get("body") or "").strip()
    device_id = (data.get("device_id") or "").strip()[:64]
    target_id = data.get("receiver_id")

    if not body:
        return jsonify({"ok": False}), 400

    receiver_id = None
    if not auth_disabled:
        try:
            receiver_id = int(target_id)
        except (TypeError, ValueError):
            return jsonify({"ok": False}), 400
        if receiver_id == current_user.id or not User.query.get(receiver_id):
            return jsonify({"ok": False}), 404

    msg = RestMessage(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        sender_device=device_id,
        body=body[:2000],
        created_at=get_ist_now(),
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"ok": True, "id": msg.id})


@rest_bp.route("/ping", methods=["POST"])
@login_required
def ping_location():
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "").strip()[:64]

    try:
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
        accuracy = float(data.get("accuracy") or 0)
    except (TypeError, ValueError):
        return jsonify({"ok": False}), 400

    now_ist = get_ist_now()

    if device_id:
        dev = LiveDevice.query.filter_by(device_id=device_id).first()
        if not dev:
            dev = LiveDevice(device_id=device_id, user_id=current_user.id)
            db.session.add(dev)
        dev.user_id = current_user.id
        dev.latitude = lat
        dev.longitude = lng
        dev.accuracy = round(accuracy, 1)
        dev.updated_at = now_ist

    loc = DeviceLocation.query.filter_by(user_id=current_user.id).first()
    if not loc:
        loc = DeviceLocation(user_id=current_user.id)
        db.session.add(loc)
    loc.latitude = lat
    loc.longitude = lng
    loc.accuracy = round(accuracy, 1)
    loc.updated_at = now_ist

    db.session.commit()
    return jsonify({"ok": True})
