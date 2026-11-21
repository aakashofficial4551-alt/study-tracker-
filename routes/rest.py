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


@rest_bp.route("/feed")
@login_required
def feed():
    auth_disabled = bool(current_app.config.get("DISABLE_AUTH", False))
    device_id = (request.args.get("device_id") or "").strip()[:64]
    target_id = request.args.get("u", type=int)

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
                "date": m.created_at.strftime("%d %b") if m.created_at else "",
            }
            for m in msgs
        ]

        # Live devices active in the last 30 minutes
        cutoff = get_ist_now() - timedelta(minutes=30)
        devices = (
            LiveDevice.query
            .filter(
                LiveDevice.latitude.isnot(None),
                LiveDevice.longitude.isnot(None),
                LiveDevice.updated_at >= cutoff,
            )
            .order_by(LiveDevice.updated_at.desc())
            .all()
        )

        # Prefer showing other active device(s); fallback to any active device
        locations = [
            {
                "mine": bool(device_id and d.device_id == device_id),
                "latitude": d.latitude,
                "longitude": d.longitude,
                "accuracy": d.accuracy,
                "address": d.address or "",
                "updated_at": d.updated_at.strftime("%I:%M %p") if d.updated_at else "",
            }
            for d in devices
        ]

        return jsonify({"items": items, "locations": locations})

    # Authenticated 1-on-1 mode (when DISABLE_AUTH = False)
    if not target_id or target_id == current_user.id:
        return jsonify({"items": [], "locations": []})

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
            "date": m.created_at.strftime("%d %b") if m.created_at else "",
        }
        for m in msgs
    ]

    peer_loc = DeviceLocation.query.filter_by(user_id=target_id).first()
    locations = []
    if peer_loc and peer_loc.latitude is not None and peer_loc.longitude is not None:
        locations.append({
            "mine": False,
            "latitude": peer_loc.latitude,
            "longitude": peer_loc.longitude,
            "accuracy": peer_loc.accuracy,
            "address": peer_loc.address or "",
            "updated_at": peer_loc.updated_at.strftime("%d %b, %I:%M %p") if peer_loc.updated_at else "",
        })

    return jsonify({"items": items, "locations": locations})


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

    address = (data.get("address") or "").strip()[:300]
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
        if address:
            dev.address = address
        dev.updated_at = now_ist

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
    return jsonify({"ok": True, "updated_at": now_ist.strftime("%I:%M %p")})
