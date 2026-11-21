from datetime import datetime
from extensions import db


class DeviceLocation(db.Model):
    __tablename__ = "device_locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(300), default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
