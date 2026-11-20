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
        "focus": "Push Upper Body",
        "exercises": [
            {"name": "Flat Bench Press", "sets": "4 sets x 8-12 reps"},
            {"name": "Incline Dumbbell Press", "sets": "3 sets x 10-12 reps"},
            {"name": "Dumbbell / Cable Chest Fly", "sets": "3 sets x 12-15 reps"},
            {"name": "Push-Ups", "sets": "3 sets x Failure"},
            {"name": "Tricep Rope Pushdown", "sets": "3 sets x 12-15 reps"},
            {"name": "Overhead Tricep Extension", "sets": "3 sets x 10-12 reps"},
            {"name": "Bench / Parallel Dips", "sets": "3 sets x 10-12 reps"},
        ],
    },
    2: {
        "title": "Back & Biceps",
        "focus": "Pull Upper Body",
        "exercises": [
            {"name": "Pull-Ups / Lat Pulldown", "sets": "4 sets x 8-12 reps"},
            {"name": "Barbell / Dumbbell Row", "sets": "4 sets x 8-12 reps"},
            {"name": "Seated Cable Row", "sets": "3 sets x 10-12 reps"},
            {"name": "Face Pulls", "sets": "3 sets x 15 reps"},
            {"name": "Barbell / EZ-Bar Bicep Curl", "sets": "3 sets x 10-12 reps"},
            {"name": "Hammer Curls", "sets": "3 sets x 12 reps"},
            {"name": "Concentration / Preacher Curl", "sets": "3 sets x 12 reps"},
        ],
    },
    3: {
        "title": "Shoulder & Abs",
        "focus": "Delts & Core",
        "exercises": [
            {"name": "Overhead Shoulder Press", "sets": "4 sets x 8-12 reps"},
            {"name": "Dumbbell Lateral Raises", "sets": "4 sets x 12-15 reps"},
            {"name": "Front Raises", "sets": "3 sets x 12 reps"},
            {"name": "Rear Delt Fly", "sets": "3 sets x 12-15 reps"},
            {"name": "Dumbbell Shrugs", "sets": "3 sets x 15 reps"},
            {"name": "Hanging Leg Raises", "sets": "3 sets x 12-15 reps"},
            {"name": "Plank", "sets": "3 sets x 60 sec"},
            {"name": "Crunches / Russian Twists", "sets": "3 sets x 20 reps"},
        ],
    },
    4: {
        "title": "Legs & Squats",
        "focus": "Lower Body Power",
        "exercises": [
            {"name": "Barbell / Bodyweight Squats", "sets": "4 sets x 8-12 reps"},
            {"name": "Leg Press", "sets": "3 sets x 10-12 reps"},
            {"name": "Walking Lunges", "sets": "3 sets x 12 reps/leg"},
            {"name": "Leg Extensions", "sets": "3 sets x 12-15 reps"},
            {"name": "Hamstring Curls", "sets": "3 sets x 12-15 reps"},
            {"name": "Standing Calf Raises", "sets": "4 sets x 15-20 reps"},
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
    next_day = 1
    if last_log:
        next_day = (last_log.day_number % 4) + 1

    active_day = request.args.get("day", type=int) or next_day
    if active_day not in WORKOUT_PLAN:
        active_day = 1

    return render_template(
        "gym/index.html",
        plan=WORKOUT_PLAN,
        active_day=active_day,
        next_day=next_day,
        last_log=last_log,
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

    flash(
        f"Day {day_number} ({plan_day['title']}) workout saved!",
        "success"
    )
    return redirect(url_for("gym.index", day=(day_number % 4) + 1))


@gym_bp.route("/delete/<int:id>")
@login_required
def delete_log(id):
    log = GymLog.query.get_or_404(id)
    if log.user_id == current_user.id:
        db.session.delete(log)
        db.session.commit()
        flash("Workout log deleted.", "info")
    return redirect(url_for("gym.index"))
