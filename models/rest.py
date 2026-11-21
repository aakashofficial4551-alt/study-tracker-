from datetime import datetime
from extensions import db


class RestMessage(db.Model):
    __tablename__ = "rest_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False, index=True)
    receiver_id = db.Column(db.Integer, nullable=True, index=True)  # None in open mode
    sender_device = db.Column(db.String(64), default="", index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LiveDevice(db.Model):
    __tablename__ = "live_devices"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(300), default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
