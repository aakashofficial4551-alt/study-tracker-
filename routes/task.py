from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models.task import Task
from models.subject import Subject

task_bp = Blueprint(
    "task",
    __name__,
    url_prefix="/tasks"
)


@task_bp.route("/")
@login_required
def home():

    tasks = (
        Task.query
        .filter_by(user_id=current_user.id)
        .order_by(Task.completed, Task.created_at.desc())
        .all()
    )

    subjects = Subject.query.order_by(
        Subject.name
    ).all()

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        subjects=subjects
    )


@task_bp.route("/add", methods=["POST"])
@login_required
def add():

    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")
    subject_id = request.form.get("subject_id")

    if not title:
        return redirect(url_for("task.home"))

    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date if due_date else None,
        subject_id=int(subject_id) if subject_id else None,
        user_id=current_user.id
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for("task.home"))


@task_bp.route("/complete/<int:id>")
@login_required
def complete(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect(url_for("task.home"))

    task.completed = True

    db.session.commit()

    return redirect(url_for("task.home"))


@task_bp.route("/delete/<int:id>")
@login_required
def delete(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect(url_for("task.home"))

    db.session.delete(task)

    db.session.commit()

    return redirect(url_for("task.home"))