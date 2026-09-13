from extensions import db


class Chapter(db.Model):

    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    completed = db.Column(db.Boolean, default=False)

    progress = db.Column(db.Integer, default=0)

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Chapter {self.name}>"