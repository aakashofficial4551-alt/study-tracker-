from datetime import datetime

from extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    priority = db.Column(
        db.String(20),
        default="Medium"
    )

    due_date = db.Column(
        db.Date
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id")
    )

    subject = db.relationship(
        "Subject",
        backref="tasks"
    )

    def __repr__(self):
        return f"<Task {self.title}>"