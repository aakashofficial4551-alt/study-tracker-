from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Subject, Chapter

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


@dashboard_bp.route("/")
@login_required
def dashboard():

    total_subjects = Subject.query.count()

    total_chapters = Chapter.query.count()

    completed_chapters = Chapter.query.filter_by(
        completed=True
    ).count()

    pending_chapters = total_chapters - completed_chapters

    if total_chapters == 0:
        progress = 0
    else:
        progress = round(
            (completed_chapters / total_chapters) * 100
        )

    recent_subjects = (
        Subject.query
        .order_by(Subject.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/dashboard.html",
        title="Dashboard",
        user=current_user,
        total_subjects=total_subjects,
        total_chapters=total_chapters,
        completed_chapters=completed_chapters,
        pending_chapters=pending_chapters,
        progress=progress,
        recent_subjects=recent_subjects,
    )