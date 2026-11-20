from datetime import datetime, timedelta
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


def build_period_stats(all_logs, today_date, days_count):
    start_date = today_date - timedelta(days=days_count - 1)
    period_logs = [l for l in all_logs if start_date <= l.log_date <= today_date]
    logged_days = len(period_logs)

    if logged_days == 0:
        return {
            "days_window": days_count,
            "logged_days": 0,
            "avg_score": 0,
            "study_days": 0,
            "gym_days": 0,
            "running_days": 0,
            "diet_days": 0,
            "sleep_days": 0,
            "bath_days": 0,
            "insta_days": 0,
            "better_days": 0,
            "clean_bad_habit": 0,
            "clean_junk_food": 0,
            "clean_social_media": 0,
            "total_study_hrs": 0.0,
            "total_gym_mins": 0,
            "total_run_mins": 0,
            "avg_sleep_hrs": 0.0,
            "total_sm_mins": 0,
        }

    return {
        "days_window": days_count,
        "logged_days": logged_days,
        "avg_score": round(sum(l.score or 0 for l in period_logs) / logged_days),
        "study_days": sum(1 for l in period_logs if l.study),
        "gym_days": sum(1 for l in period_logs if l.gym),
        "running_days": sum(1 for l in period_logs if l.running),
        "diet_days": sum(1 for l in period_logs if l.diet),
        "sleep_days": sum(1 for l in period_logs if l.sleep),
        "bath_days": sum(1 for l in period_logs if l.bath),
        "insta_days": sum(1 for l in period_logs if l.insta_upload),
        "better_days": sum(1 for l in period_logs if l.better_than_yesterday),
        "clean_bad_habit": sum(1 for l in period_logs if not l.bad_habit),
        "clean_junk_food": sum(1 for l in period_logs if not l.junk_food),
        "clean_social_media": sum(1 for l in period_logs if not l.social_media),
        "total_study_hrs": round(sum(l.study_hours or 0 for l in period_logs), 1),
        "total_gym_mins": sum(l.gym_mins or 0 for l in period_logs),
        "total_run_mins": sum(l.running_mins or 0 for l in period_logs),
        "avg_sleep_hrs": round(sum(l.sleep_hours or 0 for l in period_logs) / logged_days, 1),
        "total_sm_mins": sum(l.social_media_mins or 0 for l in period_logs),
    }


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

    all_logs = (
        DailyProgress.query
        .filter_by(user_id=current_user.id)
        .order_by(DailyProgress.log_date.desc())
        .all()
    )

    week_stats = build_period_stats(all_logs, today, 7)
    month_stats = build_period_stats(all_logs, today, 30)
    year_stats = build_period_stats(all_logs, today, 365)
    streak = calculate_streak(current_user.id, today)

    return render_template(
        "habits/daily.html",
        entry=entry,
        selected_date=selected_date,
        today=today,
        recent_logs=all_logs[:30],
        week_stats=week_stats,
        month_stats=month_stats,
        year_stats=year_stats,
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

    entry.bad_habit = parse_bool(request.form.get("bad_habit"))
    entry.junk_food = parse_bool(request.form.get("junk_food"))
    entry.social_media = parse_bool(request.form.get("social_media"))

    entry.study_hours = float(request.form.get("study_hours") or 0)
    entry.gym_mins = int(request.form.get("gym_mins") or 0)
    entry.running_mins = int(request.form.get("running_mins") or 0)
    entry.sleep_hours = float(request.form.get("sleep_hours") or 0)
    entry.social_media_mins = int(request.form.get("social_media_mins") or 0)

    entry.thoughts = (request.form.get("thoughts") or "").strip()
    entry.regret = (request.form.get("regret") or "").strip()

    entry.calculate_score()

    db.session.commit()
    flash(
        f"Task & Progress saved for {selected_date.strftime('%d %b %Y')} (Score: {entry.score}%)",
        "success"
    )
    return redirect(url_for("habits.daily_tracker", date=selected_date.isoformat()))
