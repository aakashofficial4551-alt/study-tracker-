from extensions import db
from datetime import datetime


class CalendarEvent(db.Model):

    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        default=""
    )

    event_date = db.Column(
        db.Date,
        nullable=False
    )

    event_time = db.Column(
        db.String(20),
        default=""
    )

    event_type = db.Column(
        db.String(50),
        default="Study"
    )

    color = db.Column(
        db.String(20),
        default="#3B82F6"
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<CalendarEvent {self.title}>"