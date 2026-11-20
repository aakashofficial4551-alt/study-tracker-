from datetime import datetime, date
from extensions import db


class GymLog(db.Model):
    __tablename__ = "gym_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    workout_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    day_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    day_title = db.Column(db.String(100), nullable=False)
    exercises_done = db.Column(db.Text, default="")
    completed_count = db.Column(db.Integer, default=0)
    total_count = db.Column(db.Integer, default=0)
    duration_mins = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
