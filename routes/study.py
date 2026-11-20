from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.study_session import StudySession

study_bp = Blueprint(
    "study",
    __name__,
    url_prefix="/study"
)


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


def format_duration(seconds):
    seconds = int(seconds or 0)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hrs > 0:
        parts.append(f"{hrs} {'hr' if hrs == 1 else 'hrs'}")
    if mins > 0:
        parts.append(f"{mins} {'min' if mins == 1 else 'mins'}")
    if not parts:
        parts.append(f"{secs} secs")
    return " ".join(parts)


@study_bp.route("/")
@login_required
def home():
    sessions = (
        StudySession.query
        .filter_by(user_id=current_user.id)
        .order_by(StudySession.id.desc())
        .limit(50)
        .all()
    )

    records = []
    study_total_secs = 0
    running_total_secs = 0

    for s in sessions:
        mode_raw = (s.subject or "Study Mode").strip()
        is_running = "running" in mode_raw.lower()
        mode_label = "Running Mode" if is_running else "Study Mode"

        if is_running:
            running_total_secs += (s.duration or 0)
        else:
            study_total_secs += (s.duration or 0)

        date_str = s.start_time.strftime("%d %b %Y") if s.start_time else "Today"

        records.append({
            "id": s.id,
            "date": date_str,
            "duration_text": format_duration(s.duration or 0),
            "mode": mode_label,
            "is_running": is_running,
        })

    return render_template(
        "study/index.html",
        records=records,
        study_total_text=format_duration(study_total_secs),
        running_total_text=format_duration(running_total_secs),
    )


@study_bp.route("/save", methods=["POST"])
@login_required
def save():
    mode = request.form.get("mode", "study").strip().lower()
    mode_label = "Running Mode" if mode == "running" else "Study Mode"

    duration = int(request.form.get("duration") or 0)
    quick_mins = request.form.get("quick_mins")

    if quick_mins:
        try:
            duration = int(float(quick_mins) * 60)
        except ValueError:
            duration = 0

    if duration <= 0:
        flash("Timer 0 sec par hai — pehle timer chalao ya minutes daalo.", "warning")
        return redirect(url_for("study.home"))

    now_ist = get_ist_now()

    session = StudySession(
        user_id=current_user.id,
        subject=mode_label,
        chapter="",
        duration=duration,
        notes="",
        rating=5,
        completed=True,
        start_time=now_ist,
        end_time=now_ist,
    )

    db.session.add(session)
    db.session.commit()

    flash(f"Saved: {format_duration(duration)} • {mode_label}", "success")
    return redirect(url_for("study.home"))


@study_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    session = StudySession.query.get_or_404(id)
    if session.user_id == current_user.id:
        db.session.delete(session)
        db.session.commit()
        flash("Record deleted.", "info")
    return redirect(url_for("study.home"))
