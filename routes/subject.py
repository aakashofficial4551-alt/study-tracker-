from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import Subject

subject_bp = Blueprint(
    "subject",
    __name__,
    url_prefix="/subjects"
)


@subject_bp.route("/")
def subjects():

    all_subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        "subjects/index.html",
        subjects=all_subjects
    )


@subject_bp.route("/add", methods=["POST"])
def add_subject():

    name = request.form.get("name")

    icon = request.form.get("icon")

    color = request.form.get("color")

    chapters = request.form.get("chapters")

    if not name:
        return redirect(url_for("subject.subjects"))

    new_subject = Subject(
        name=name,
        icon=icon,
        color=color,
        total_chapters=int(chapters)
    )

    db.session.add(new_subject)

    db.session.commit()

    return redirect(url_for("subject.subjects"))


@subject_bp.route("/delete/<int:id>")
def delete_subject(id):

    subject = Subject.query.get_or_404(id)

    db.session.delete(subject)

    db.session.commit()

    return redirect(url_for("subject.subjects"))