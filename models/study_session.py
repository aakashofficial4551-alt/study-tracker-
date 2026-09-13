from extensions import db
from datetime import datetime


class StudySession(db.Model):

    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    subject = db.Column(db.String(100), nullable=False)

    chapter = db.Column(db.String(200))

    duration = db.Column(db.Integer, default=0)

    date = db.Column(
        db.Date,
        default=datetime.utcnow
    )

    start_time = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    end_time = db.Column(db.DateTime)

    completed = db.Column(
        db.Boolean,
        default=False
    )

    notes = db.Column(db.Text)

    rating = db.Column(db.Integer, default=5)