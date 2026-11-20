from datetime import datetime, date
from extensions import db


class TestRecord(db.Model):
    __tablename__ = "test_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    test_name = db.Column(db.String(150), nullable=False)
    test_date = db.Column(db.Date, nullable=False, default=date.today)
    test_time = db.Column(db.String(20), default="")
    subject_name = db.Column(db.String(100), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False, default=0.0)
    total_marks = db.Column(db.Float, nullable=False, default=100.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def percentage(self):
        if not self.total_marks or self.total_marks <= 0:
            return 0
        return round((self.marks_obtained / self.total_marks) * 100, 1)
