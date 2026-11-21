from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Subject
from models.topic import SyllabusChapter, THEORY_MARKS_MAP, seed_cbse_syllabus
from models.mock_test import TestRecord

subject_bp = Blueprint(
    "subject",
    __name__,
    url_prefix="/subjects"
)


def get_ist_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


@subject_bp.route("/")
@login_required
def subjects():
    seed_cbse_syllabus()
    now_ist = get_ist_now()

    all_subjects = Subject.query.order_by(Subject.id.asc()).all()
    all_chapters = SyllabusChapter.query.order_by(
        SyllabusChapter.subject_name.asc(),
        SyllabusChapter.chapter_number.asc()
    ).all()

    chapters_by_subject = {}
    for ch in all_chapters:
        chapters_by_subject.setdefault(ch.subject_name, []).append(ch)

    syllabus_blocks = []
    for s in all_subjects:
        ch_list = chapters_by_subject.get(s.name, [])
        done_count = sum(1 for c in ch_list if c.completed)
        total_count = len(ch_list)
        pct = round((done_count / total_count) * 100) if total_count > 0 else 0
        syllabus_blocks.append({
            "subject": s,
            "theory_marks": THEORY_MARKS_MAP.get(s.name),
            "chapters": ch_list,
            "done": done_count,
            "total": total_count,
            "pct": pct,
        })

    total_subjects = len(all_subjects)
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
        syllabus_blocks=syllabus_blocks,
        total_subjects=total_subjects,
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
    ch = SyllabusChapter.query.get_or_404(id)
    ch.completed = not ch.completed
    db.session.commit()

    subj_chapters = SyllabusChapter.query.filter_by(subject_name=ch.subject_name).all()
    subj_done = sum(1 for c in subj_chapters if c.completed)
    subj_total = len(subj_chapters)
    subj_pct = round((subj_done / subj_total) * 100) if subj_total > 0 else 0

    total_all = SyllabusChapter.query.count()
    done_all = SyllabusChapter.query.filter_by(completed=True).count()
    overall_pct = round((done_all / total_all) * 100) if total_all > 0 else 0

    return jsonify({
        "ok": True,
        "completed": ch.completed,
        "subject_name": ch.subject_name,
        "subj_done": subj_done,
        "subj_total": subj_total,
        "subj_pct": subj_pct,
        "done_all": done_all,
        "total_all": total_all,
        "pending_all": total_all - done_all,
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
    SyllabusChapter.query.filter_by(subject_name=subject.name).delete()
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
