from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Subject, Chapter
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
    today = get_ist_today()

    # 1. Daily Task & Streak
    today_log = DailyProgress.query.filter_by(
        user_id=current_user.id,
        log_date=today
    ).first()

    all_daily = (
        DailyProgress.query
        .filter_by(user_id=current_user.id)
        .order_by(DailyProgress.log_date.desc())
        .all()
    )

    log_dates = {l.log_date for l in all_daily}
    streak = 0
    check_date = today if today in log_dates else today - timedelta(days=1)
    while check_date in log_dates:
        streak += 1
        check_date -= timedelta(days=1)

    today_score = today_log.score if today_log else 0

    # 2. Timer Summary (Study vs Running)
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

    # 3. Gym Next Split
    last_gym = (
        GymLog.query
        .filter_by(user_id=current_user.id)
        .order_by(GymLog.workout_date.desc(), GymLog.id.desc())
        .first()
    )
    next_gym_day = ((last_gym.day_number % 4) + 1) if last_gym else 1
    next_gym_title = GYM_SPLIT_NAMES[next_gym_day]

    # 4. Subjects & Chapters
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    completed_chapters = Chapter.query.filter_by(completed=True).count()
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
        streak=streak,
        study_time_str=format_short_time(study_secs),
        running_time_str=format_short_time(running_secs),
        last_gym=last_gym,
        next_gym_day=next_gym_day,
        next_gym_title=next_gym_title,
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        syllabus_progress=syllabus_progress,
    )
