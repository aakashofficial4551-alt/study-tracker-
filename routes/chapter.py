from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import Subject, Chapter

chapter_bp = Blueprint(
    "chapter",
    __name__,
    url_prefix="/chapters"
)


@chapter_bp.route("/<int:subject_id>")
def view(subject_id):

    subject = Subject.query.get_or_404(subject_id)

    chapters = Chapter.query.filter_by(
        subject_id=subject.id
    ).all()

    return render_template(
        "chapters/index.html",
        subject=subject,
        chapters=chapters
    )


@chapter_bp.route("/add/<int:subject_id>", methods=["POST"])
def add(subject_id):

    name = request.form.get("name")

    if not name:
        return redirect(
            url_for(
                "chapter.view",
                subject_id=subject_id
            )
        )

    chapter = Chapter(
        name=name,
        subject_id=subject_id
    )

    db.session.add(chapter)

    subject = Subject.query.get(subject_id)

    subject.total_chapters += 1

    db.session.commit()

    return redirect(
        url_for(
            "chapter.view",
            subject_id=subject_id
        )
    )


@chapter_bp.route("/complete/<int:id>")
def complete(id):

    chapter = Chapter.query.get_or_404(id)

    if not chapter.completed:

        chapter.completed = True

        chapter.subject.completed_chapters += 1

        db.session.commit()

    return redirect(
        url_for(
            "chapter.view",
            subject_id=chapter.subject_id
        )
    )


@chapter_bp.route("/delete/<int:id>")
def delete(id):

    chapter = Chapter.query.get_or_404(id)

    subject = chapter.subject

    if chapter.completed:
        subject.completed_chapters -= 1

    subject.total_chapters -= 1

    db.session.delete(chapter)

    db.session.commit()

    return redirect(
        url_for(
            "chapter.view",
            subject_id=subject.id
        )
    )