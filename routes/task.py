from flask import Blueprint, redirect, url_for
from flask_login import login_required

task_bp = Blueprint(
    "task",
    __name__,
    url_prefix="/tasks"
)


@task_bp.route("/")
@login_required
def home():
    return redirect(url_for("habits.daily_tracker"))
