from extensions import db


class SyllabusChapter(db.Model):
    __tablename__ = "syllabus_chapters"

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False, index=True)
    theory_marks = db.Column(db.Integer, nullable=False, default=70)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
