from extensions import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    icon = db.Column(
        db.String(20),
        default="📚"
    )

    color = db.Column(
        db.String(20),
        default="#3B82F6"
    )

    description = db.Column(
        db.String(500),
        default=""
    )

    total_chapters = db.Column(
        db.Integer,
        default=0
    )

    completed_chapters = db.Column(
        db.Integer,
        default=0
    )

    total_study_minutes = db.Column(
        db.Integer,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    chapters = db.relationship(
        "Chapter",
        backref="subject",
        lazy=True,
        cascade="all, delete"
    )

    @property
    def progress(self):
        if self.total_chapters == 0:
            return 0

        return int(
            (self.completed_chapters / self.total_chapters) * 100
        )

    def __repr__(self):
        return f"<Subject {self.name}>"