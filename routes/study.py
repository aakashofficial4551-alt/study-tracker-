from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.study_session import StudySession
from models.subject import Subject
from datetime import datetime

study_bp = Blueprint(
    "study",
    __name__,
    url_prefix="/study"
)


@study_bp.route("/")
@login_required
def home():

    subjects = Subject.query.order_by(Subject.name).all()

    sessions = (
        StudySession.query
        .filter_by(user_id=current_user.id)
        .order_by(StudySession.id.desc())
        .limit(20)
        .all()
    )

    total_seconds = sum(s.duration or 0 for s in sessions)

    total_hours = round(total_seconds / 3600, 2)

    return render_template(
        "study/index.html",
        subjects=subjects,
        sessions=sessions,
        total_seconds=total_seconds,
        total_hours=total_hours
    )


@study_bp.route("/save", methods=["POST"])
@login_required
def save():

    subject = request.form.get("subject")
    chapter = request.form.get("chapter")
    notes = request.form.get("notes")

    duration = int(request.form.get("duration") or 0)

    rating = int(request.form.get("rating") or 5)

    session = StudySession(
        user_id=current_user.id,
        subject=subject,
        chapter=chapter,
        duration=duration,
        notes=notes,
        rating=rating,
        completed=True,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow()
    )

    db.session.add(session)
    db.session.commit()

    return redirect(url_for("study.home"))