from datetime import datetime, date
from extensions import db


class DailyProgress(db.Model):
    __tablename__ = "daily_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    # Positive Daily Ticks (True = Done / Yes)
    study = db.Column(db.Boolean, default=False)
    gym = db.Column(db.Boolean, default=False)
    running = db.Column(db.Boolean, default=False)
    diet = db.Column(db.Boolean, default=False)
    sleep = db.Column(db.Boolean, default=False)
    bath = db.Column(db.Boolean, default=False)
    insta_upload = db.Column(db.Boolean, default=False)
    better_than_yesterday = db.Column(db.Boolean, default=False)

    # Control / Avoidance Checks (True = Yes kiya, False = Avoid kiya)
    bad_habit = db.Column(db.Boolean, default=False)
    junk_food = db.Column(db.Boolean, default=False)
    social_media = db.Column(db.Boolean, default=False)

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
        # 11 total points: 8 positive checks (True = +1) + 3 control checks (False = +1)
        points = 0
        positive_fields = [
            self.study,
            self.gym,
            self.running,
            self.diet,
            self.sleep,
            self.bath,
            self.insta_upload,
            self.better_than_yesterday,
        ]
        avoid_fields = [
            self.bad_habit,
            self.junk_food,
            self.social_media,
        ]

        points += sum(1 for item in positive_fields if item)
        points += sum(1 for item in avoid_fields if not item)

        self.score = round((points / 11) * 100)
        return self.score
