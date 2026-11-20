from datetime import datetime, date
from extensions import db


class DailyProgress(db.Model):
    __tablename__ = "daily_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    # Positive Daily Ticks (True = Ticked)
    study = db.Column(db.Boolean, default=False)
    gym = db.Column(db.Boolean, default=False)
    running = db.Column(db.Boolean, default=False)
    diet = db.Column(db.Boolean, default=False)
    sleep = db.Column(db.Boolean, default=False)
    bath = db.Column(db.Boolean, default=False)
    learn_new = db.Column(db.Boolean, default=False)
    meditation = db.Column(db.Boolean, default=False)
    insta_upload = db.Column(db.Boolean, default=False)
    better_than_yesterday = db.Column(db.Boolean, default=False)

    # Stored as False when user ticks "No Bad Habits / No Junk Food / No Social Media"
    bad_habit = db.Column(db.Boolean, default=True)
    junk_food = db.Column(db.Boolean, default=True)
    social_media = db.Column(db.Boolean, default=True)

    # Separate Side Panel: Time Tracking
    study_hours = db.Column(db.Float, default=0.0)
    gym_mins = db.Column(db.Integer, default=0)
    running_mins = db.Column(db.Integer, default=0)
    sleep_hours = db.Column(db.Float, default=0.0)
    social_media_mins = db.Column(db.Integer, default=0)

    # Daily Reflections
    thoughts = db.Column(db.Text, default="")
    regret = db.Column(db.Text, default="")

    # Auto Score (0 to 100)
    score = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "log_date", name="unique_user_daily_log"),
    )

    def calculate_score(self):
        # 13 total positive ticks
        checks = [
            bool(self.study),
            bool(self.gym),
            bool(self.running),
            bool(self.diet),
            bool(self.sleep),
            bool(self.bath),
            not bool(self.bad_habit),     # No Bad Habits
            not bool(self.junk_food),     # No Junk Food
            not bool(self.social_media),  # No Social Media
            bool(self.learn_new),         # Learn Something New
            bool(self.meditation),        # Meditation
            bool(self.insta_upload),
            bool(self.better_than_yesterday),
        ]
        points = sum(1 for item in checks if item)
        self.score = round((points / len(checks)) * 100)
        return self.score
