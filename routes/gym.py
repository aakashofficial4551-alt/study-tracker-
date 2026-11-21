from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.gym import GymLog

gym_bp = Blueprint(
    "gym",
    __name__,
    url_prefix="/gym"
)

WORKOUT_PLAN = {
    1: {
        "title": "Chest & Triceps",
        "exercises": [
            "Flat Bench Press",
            "Incline Dumbbell Press",
            "Cable Chest Fly",
            "Push-Ups",
            "Tricep Rope Pushdown",
            "Overhead Tricep Extension",
            "Dips",
        ],
    },
    2: {
        "title": "Back & Biceps",
        "exercises": [
            "Pull-Ups / Lat Pulldown",
            "Barbell / Dumbbell Row",
            "Seated Cable Row",
            "Face Pulls",
            "Barbell Bicep Curl",
            "Hammer Curls",
            "Preacher Curl",
        ],
    },
    3: {
        "title": "Shoulder & Abs",
        "exercises": [
            "Overhead Shoulder Press",
            "Lateral Raises",
            "Front Raises",
            "Rear Delt Fly",
            "Dumbbell Shrugs",
            "Hanging Leg Raises",
            "Plank",
            "Crunches",
        ],
    },
    4: {
        "title": "Legs & Squats",
        "exercises": [
            "Squats",
            "Leg Press",
            "Walking Lunges",
            "Leg Extensions",
            "Hamstring Curls",
            "Calf Raises",
        ],
    },
}


def get_ist_today():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).date()


@gym_bp.route("/")
@login_required
def index():
    today = get_ist_today()
    logs = (
        GymLog.query
        .filter_by(user_id=current_user.id)
        .order_by(GymLog.workout_date.desc(), GymLog.id.desc())
        .limit(25)
        .all()
    )

    last_log = logs[0] if logs else None
    next_day = ((last_log.day_number % 4) + 1) if last_log else 1

    active_day = request.args.get("day", type=int) or next_day
    if active_day not in WORKOUT_PLAN:
        active_day = 1

    return render_template(
        "gym/index.html",
        plan=WORKOUT_PLAN,
        active_day=active_day,
        logs=logs,
        today=today,
    )


@gym_bp.route("/log", methods=["POST"])
@login_required
def log_workout():
    day_number = int(request.form.get("day_number") or 1)
    if day_number not in WORKOUT_PLAN:
        day_number = 1

    plan_day = WORKOUT_PLAN[day_number]
    checked = request.form.getlist("exercises")
    duration_mins = int(request.form.get("duration_mins") or 0)
    notes = (request.form.get("notes") or "").strip()
    date_str = request.form.get("workout_date")

    try:
        workout_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else get_ist_today()
        )
    except ValueError:
        workout_date = get_ist_today()

    new_log = GymLog(
        user_id=current_user.id,
        workout_date=workout_date,
        day_number=day_number,
        day_title=plan_day["title"],
        exercises_done=", ".join(checked),
        completed_count=len(checked),
        total_count=len(plan_day["exercises"]),
        duration_mins=duration_mins,
        notes=notes,
    )

    db.session.add(new_log)
    db.session.commit()

    flash("Saved.", "success")
    return redirect(url_for("gym.index", day=(day_number % 4) + 1))


@gym_bp.route("/delete/<int:id>")
@login_required
def delete_log(id):
    log = GymLog.query.get_or_404(id)
    if log.user_id == current_user.id:
        db.session.delete(log)
        db.session.commit()
        flash("Deleted.", "info")
    return redirect(url_for("gym.index"))
