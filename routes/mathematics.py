from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.core import Subject, Chapter
from models.mathematics import MathTheorem, MathShortcut, MathFormula

math_bp = Blueprint('math', __name__)

@math_bp.route('/')
@math_bp.route('/hub')
@login_required
def hub():
    """Mathematics Subject Hub tracking Theorems, Calculus formulas, and Shortcuts."""
    subject = Subject.query.filter_by(name='Mathematics').first()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() if subject else []

    chapter_ids = [c.id for c in chapters]
    theorems = MathTheorem.query.filter(MathTheorem.chapter_id.in_(chapter_ids)).all() if chapter_ids else []
    shortcuts = MathShortcut.query.filter(MathShortcut.chapter_id.in_(chapter_ids)).all() if chapter_ids else []
    formulas = MathFormula.query.filter(MathFormula.chapter_id.in_(chapter_ids)).all() if chapter_ids else []

    return render_template('subjects/math_hub.html',
                           subject=subject,
                           chapters=chapters,
                           theorems=theorems,
                           shortcuts=shortcuts,
                           formulas=formulas)

@math_bp.route('/formula/add', methods=['POST'])
@login_required
def add_formula():
    chapter_id = request.form.get('chapter_id')
    topic = request.form.get('topic').strip()
    formula_name = request.form.get('formula_name').strip()
    formula_latex = request.form.get('formula_latex').strip()

    if not chapter_id or not formula_name or not formula_latex:
        flash('Chapter, formula name, and LaTeX notation are required.', 'danger')
        return redirect(url_for('math.hub'))

    formula = MathFormula(
        chapter_id=chapter_id,
        topic=topic,
        formula_name=formula_name,
        formula_latex=formula_latex
    )
    db.session.add(formula)
    db.session.commit()
    flash('Math formula added!', 'success')
    return redirect(url_for('math.hub'))