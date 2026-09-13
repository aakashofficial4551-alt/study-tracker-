from flask import Blueprint, render_template
from flask_login import login_required
from models.subject import Subject
from models.chapter import Chapter

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


@analytics_bp.route("/")
@login_required
def home():

    total_subjects = Subject.query.count()

    total_chapters = Chapter.query.count()

    completed = Chapter.query.filter_by(
        completed=True
    ).count()

    pending = total_chapters - completed

    if total_chapters == 0:
        progress = 0
    else:
        progress = int(
            (completed / total_chapters) * 100
        )

    return render_template(
        "analytics/index.html",
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        completed=completed,
        pending=pending,
        progress=progress
    )