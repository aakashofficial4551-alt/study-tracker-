from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.habits import DailyProgress

habits_bp = Blueprint(
    "habits",
    __name__,
    url_prefix="/daily"
)


def get_ist_today():
    """Render UTC par chalta hai, ye India (IST) ki exact date deta hai."""
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()


def parse_bool(value):
    return str(value).lower() in ("yes", "true", "1", "on")


def calculate_streak(user_id, today_date):
    logs = (
        DailyProgress.query
        .filter_by(user_id=user_id)
        .order_by(DailyProgress.log_date.desc())
        .all()
    )
    if not logs:
        return 0

    log_dates = {log.log_date for log in logs}
    streak = 0
    check_date = today_date if today_date in log_dates else today_date - timedelta(days=1)

    while check_date in log_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


@habits_bp.route("/")
@login_required
def daily_tracker():
    today = get_ist_today()
    date_str = request.args.get("date")

    try:
        selected_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else today
        )
    except ValueError:
        selected_date = today

    entry = DailyProgress.query.filter_by(
        user_id=current_user.id,
        log_date=selected_date
    ).first()

    recent_logs = (
        DailyProgress.query
        .filter_by(user_id=current_user.id)
        .order_by(DailyProgress.log_date.desc())
        .limit(14)
        .all()
    )

    last_7 = recent_logs[:7]
    avg_score = round(sum(l.score for l in last_7) / len(last_7)) if last_7 else 0
    total_study_7d = round(sum(l.study_hours or 0 for l in last_7), 1)
    streak = calculate_streak(current_user.id, today)

    return render_template(
        "habits/daily.html",
        entry=entry,
        selected_date=selected_date,
        today=today,
        recent_logs=recent_logs,
        avg_score=avg_score,
        total_study_7d=total_study_7d,
        streak=streak,
    )


@habits_bp.route("/save", methods=["POST"])
@login_required
def save_daily():
    today = get_ist_today()
    date_str = request.form.get("log_date")

    try:
        selected_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else today
        )
    except ValueError:
        selected_date = today

    entry = DailyProgress.query.filter_by(
        user_id=current_user.id,
        log_date=selected_date
    ).first()

    if not entry:
        entry = DailyProgress(
            user_id=current_user.id,
            log_date=selected_date
        )
        db.session.add(entry)

    # Checklist Ticks
    entry.study = parse_bool(request.form.get("study"))
    entry.gym = parse_bool(request.form.get("gym"))
    entry.running = parse_bool(request.form.get("running"))
    entry.diet = parse_bool(request.form.get("diet"))
    entry.sleep = parse_bool(request.form.get("sleep"))
    entry.bath = parse_bool(request.form.get("bath"))
    entry.insta_upload = parse_bool(request.form.get("insta_upload"))
    entry.better_than_yesterday = parse_bool(
        request.form.get("better_than_yesterday")
    )

    # Control / Avoidance Ticks
    entry.bad_habit = parse_bool(request.form.get("bad_habit"))
    entry.junk_food = parse_bool(request.form.get("junk_food"))
    entry.social_media = parse_bool(request.form.get("social_media"))

    # Time Tracking (Side Panel)
    entry.study_hours = float(request.form.get("study_hours") or 0)
    entry.gym_mins = int(request.form.get("gym_mins") or 0)
    entry.running_mins = int(request.form.get("running_mins") or 0)
    entry.sleep_hours = float(request.form.get("sleep_hours") or 0)
    entry.social_media_mins = int(request.form.get("social_media_mins") or 0)

    # Reflections
    entry.thoughts = (request.form.get("thoughts") or "").strip()
    entry.regret = (request.form.get("regret") or "").strip()

    # Recalculate Score
    entry.calculate_score()

    db.session.commit()
    flash(
        f"Progress saved for {selected_date.strftime('%d %b %Y')}! Score: {entry.score}%",
        "success"
    )
    return redirect(url_for("habits.daily_tracker", date=selected_date.isoformat()))
