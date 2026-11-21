from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Subject
from models.topic import SyllabusChapter, seed_cbse_syllabus
from models.habits import DailyProgress
from models.study_session import StudySession
from models.gym import GymLog

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

GYM_SPLIT_NAMES = {
    1: "Chest & Triceps",
    2: "Back & Biceps",
    3: "Shoulder & Abs",
    4: "Legs & Squats",
}


def get_ist_today():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()


def format_short_time(total_seconds):
    total_seconds = int(total_seconds or 0)
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    if hrs > 0 and mins > 0:
        return f"{hrs}h {mins}m"
    if hrs > 0:
        return f"{hrs} hrs"
    return f"{mins} mins"


@dashboard_bp.route("/")
@login_required
def dashboard():
    seed_cbse_syllabus()
    today = get_ist_today()

    today_log = DailyProgress.query.filter_by(
        user_id=current_user.id,
        log_date=today
    ).first()
    today_score = today_log.score if today_log else 0

    sessions = (
        StudySession.query
        .filter_by(user_id=current_user.id)
        .order_by(StudySession.id.desc())
        .all()
    )

    study_secs = sum(
        (s.duration or 0) for s in sessions
        if "running" not in (s.subject or "").lower()
    )
    running_secs = sum(
        (s.duration or 0) for s in sessions
        if "running" in (s.subject or "").lower()
    )

    last_gym = (
        GymLog.query
        .filter_by(user_id=current_user.id)
        .order_by(GymLog.workout_date.desc(), GymLog.id.desc())
        .first()
    )
    next_gym_day = ((last_gym.day_number % 4) + 1) if last_gym else 1
    next_gym_title = GYM_SPLIT_NAMES[next_gym_day]

    total_subjects = Subject.query.count()
    total_chapters = SyllabusChapter.query.count()
    completed_chapters = SyllabusChapter.query.filter_by(completed=True).count()
    syllabus_progress = (
        round((completed_chapters / total_chapters) * 100)
        if total_chapters > 0 else 0
    )

    return render_template(
        "dashboard/dashboard.html",
        title="Dashboard",
        user=current_user,
        today=today,
        today_log=today_log,
        today_score=today_score,
        study_time_str=format_short_time(study_secs),
        running_time_str=format_short_time(running_secs),
        next_gym_day=next_gym_day,
        next_gym_title=next_gym_title,
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        syllabus_progress=syllabus_progress,
    )
