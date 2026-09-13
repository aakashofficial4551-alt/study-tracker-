from extensions import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    full_name = db.Column(db.String(150))

    class_name = db.Column(db.String(20), default="Class 12")

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<User {self.username}>"