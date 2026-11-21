from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Subject
from models.syllabus import SyllabusChapter
from models.mock_test import TestRecord

subject_bp = Blueprint(
    "subject",
    __name__,
    url_prefix="/subjects"
)

CBSE_SYLLABUS = [
    {
        "subject": "Physics",
        "theory_marks": 70,
        "color": "#ff2442",
        "chapters": [
            "Electric Charges and Fields",
            "Electrostatic Potential and Capacitance",
            "Current Electricity",
            "Moving Charges and Magnetism",
            "Magnetism and Matter",
            "Electromagnetic Induction",
            "Alternating Current",
            "Electromagnetic Waves",
            "Ray Optics and Optical Instruments",
            "Wave Optics",
            "Dual Nature of Radiation and Matter",
            "Atoms",
            "Nuclei",
            "Semiconductor Electronics: Materials, Devices and Simple Circuits",
        ],
    },
    {
        "subject": "Chemistry",
        "theory_marks": 70,
        "color": "#ff2e88",
        "chapters": [
            "Solutions",
            "Electrochemistry",
            "Chemical Kinetics",
            "d- and f-Block Elements",
            "Coordination Compounds",
            "Haloalkanes and Haloarenes",
            "Alcohols, Phenols and Ethers",
            "Aldehydes, Ketones and Carboxylic Acids",
            "Amines",
            "Biomolecules",
        ],
    },
    {
        "subject": "Mathematics",
        "theory_marks": 80,
        "color": "#16c784",
        "chapters": [
            "Relations and Functions",
            "Inverse Trigonometric Functions",
            "Matrices",
            "Determinants",
            "Continuity and Differentiability",
            "Applications of Derivatives",
            "Integrals",
            "Applications of Integrals",
            "Differential Equations",
            "Vector Algebra",
            "Three Dimensional Geometry",
            "Linear Programming",
            "Probability",
        ],
    },
]


def seed_cbse_syllabus():
    """Ensures Physics, Chemistry, and Mathematics CBSE chapters exist."""
    changed = False
    for item in CBSE_SYLLABUS:
        subj_name = item["subject"]
        chapters = item["chapters"]

        existing_subj = Subject.query.filter_by(name=subj_name).first()
        if not existing_subj:
            db.session.add(
                Subject(
                    name=subj_name,
                    icon="",
                    color=item["color"],
                    total_chapters=len(chapters),
                )
            )
            changed = True

        existing_count = SyllabusChapter.query.filter_by(subject_name=subj_name).count()
        if existing_count == 0:
            for idx, title in enumerate(chapters, start=1):
                db.session.add(
                    SyllabusChapter(
                        subject_name=subj_name,
                        theory_marks=item["theory_marks"],
                        chapter_number=idx,
                        title=title,
                        completed=False,
                    )
                )
            changed = True

    if changed:
        db.session.commit()


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


@subject_bp.route("/")
@login_required
def subjects():
    seed_cbse_syllabus()

    now_ist = get_ist_now()
    all_subjects = Subject.query.order_by(Subject.name).all()
    all_chapters = SyllabusChapter.query.order_by(
        SyllabusChapter.subject_name, SyllabusChapter.chapter_number
    ).all()

    syllabus_groups = []
    for item in CBSE_SYLLABUS:
        sname = item["subject"]
        ch_list = [c for c in all_chapters if c.subject_name == sname]
        done = sum(1 for c in ch_list if c.completed)
        total = len(ch_list)
        pct = round((done / total) * 100) if total > 0 else 0
        syllabus_groups.append({
            "name": sname,
            "theory_marks": item["theory_marks"],
            "color": item["color"],
            "chapters": ch_list,
            "completed": done,
            "total": total,
            "percent": pct,
        })

    total_chapters = len(all_chapters)
    completed_chapters = sum(1 for c in all_chapters if c.completed)
    pending_chapters = total_chapters - completed_chapters
    syllabus_progress = (
        round((completed_chapters / total_chapters) * 100)
        if total_chapters > 0 else 0
    )

    tests = (
        TestRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(TestRecord.test_date.desc(), TestRecord.id.desc())
        .all()
    )

    avg_test_pct = (
        round(sum(t.percentage for t in tests) / len(tests), 1)
        if tests else 0
    )

    return render_template(
        "subjects/index.html",
        subjects=all_subjects,
        syllabus_groups=syllabus_groups,
        total_subjects=len(all_subjects),
        total_chapters=total_chapters,
        completed_chapters=completed_chapters,
        pending_chapters=pending_chapters,
        syllabus_progress=syllabus_progress,
        tests=tests,
        avg_test_pct=avg_test_pct,
        today_str=now_ist.strftime("%Y-%m-%d"),
        now_time_str=now_ist.strftime("%H:%M"),
    )


@subject_bp.route("/chapter/toggle/<int:id>", methods=["POST"])
@login_required
def toggle_chapter(id):
    chapter = SyllabusChapter.query.get_or_404(id)
    chapter.completed = not chapter.completed
    db.session.commit()

    subj_chapters = SyllabusChapter.query.filter_by(
        subject_name=chapter.subject_name
    ).all()
    subj_done = sum(1 for c in subj_chapters if c.completed)
    subj_total = len(subj_chapters)
    subj_pct = round((subj_done / subj_total) * 100) if subj_total > 0 else 0

    all_total = SyllabusChapter.query.count()
    all_done = SyllabusChapter.query.filter_by(completed=True).count()
    overall_pct = round((all_done / all_total) * 100) if all_total > 0 else 0

    return jsonify({
        "completed": chapter.completed,
        "subject_name": chapter.subject_name,
        "subject_done": subj_done,
        "subject_total": subj_total,
        "subject_pct": subj_pct,
        "all_done": all_done,
        "all_total": all_total,
        "pending": all_total - all_done,
        "overall_pct": overall_pct,
    })


@subject_bp.route("/add", methods=["POST"])
@login_required
def add_subject():
    name = (request.form.get("name") or "").strip()
    color = request.form.get("color") or "#ff2e88"
    chapters = int(request.form.get("chapters") or 0)

    if not name:
        return redirect(url_for("subject.subjects"))

    new_subject = Subject(
        name=name,
        icon="",
        color=color,
        total_chapters=chapters
    )
    db.session.add(new_subject)
    db.session.commit()
    flash("Subject added.", "success")
    return redirect(url_for("subject.subjects"))


@subject_bp.route("/delete/<int:id>")
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "info")
    return redirect(url_for("subject.subjects"))


@subject_bp.route("/test/add", methods=["POST"])
@login_required
def add_test():
    test_name = (request.form.get("test_name") or "").strip()
    date_str = request.form.get("test_date")
    test_time = (request.form.get("test_time") or "").strip()
    subject_name = (request.form.get("subject_name") or "").strip()

    try:
        marks_obtained = float(request.form.get("marks_obtained") or 0)
        total_marks = float(request.form.get("total_marks") or 100)
    except ValueError:
        flash("Enter valid marks.", "danger")
        return redirect(url_for("subject.subjects"))

    if not test_name or not subject_name:
        flash("Test name and subject are required.", "warning")
        return redirect(url_for("subject.subjects"))

    try:
        parsed_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else get_ist_now().date()
        )
    except ValueError:
        parsed_date = get_ist_now().date()

    display_time = test_time
    if test_time and ":" in test_time:
        try:
            display_time = datetime.strptime(test_time, "%H:%M").strftime("%I:%M %p")
        except ValueError:
            display_time = test_time

    record = TestRecord(
        user_id=current_user.id,
        test_name=test_name,
        test_date=parsed_date,
        test_time=display_time,
        subject_name=subject_name,
        marks_obtained=marks_obtained,
        total_marks=total_marks if total_marks > 0 else 100.0,
    )
    db.session.add(record)
    db.session.commit()
    flash("Test saved.", "success")
    return redirect(url_for("subject.subjects"))


@subject_bp.route("/test/delete/<int:id>", methods=["POST"])
@login_required
def delete_test(id):
    record = TestRecord.query.get_or_404(id)
    if record.user_id == current_user.id:
        db.session.delete(record)
        db.session.commit()
        flash("Deleted.", "info")
    return redirect(url_for("subject.subjects"))
