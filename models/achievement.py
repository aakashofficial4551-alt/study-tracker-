from datetime import datetime

from extensions import db


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text)

    icon = db.Column(db.String(100), default="🏆")

    unlocked = db.Column(db.Boolean, default=False)

    unlocked_at = db.Column(db.DateTime)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def unlock(self):
        self.unlocked = True
        self.unlocked_at = datetime.utcnow()

    def __repr__(self):
        return f"<Achievement {self.title}>"