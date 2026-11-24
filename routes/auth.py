import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, bcrypt
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        full_name = (request.form.get("full_name") or "").strip()

        if not username:
            flash("Enter username.", "warning")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()
        if not user:
            placeholder_pw = bcrypt.generate_password_hash(uuid.uuid4().hex).decode("utf-8")
            user = User(
                username=username,
                full_name=full_name or username,
                email=f"{username}@urrecords.local",
                password=placeholder_pw,
            )
            db.session.add(user)
            db.session.commit()
        elif full_name and user.full_name != full_name:
            user.full_name = full_name
            db.session.commit()

        login_user(user, remember=True)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
