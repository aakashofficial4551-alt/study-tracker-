from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.core import Subject, Chapter
from models.physics import PhysicsDerivation, PhysicsNumerical, PhysicsFormula

physics_bp = Blueprint('physics', __name__)

@physics_bp.route('/')
@physics_bp.route('/hub')
@login_required
def hub():
    """Physics Subject Hub dashboard with derivations, formulas, and progress."""
    subject = Subject.query.filter_by(name='Physics').first()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() if subject else []
    
    chapter_ids = [c.id for c in chapters]
    derivations = PhysicsDerivation.query.filter(PhysicsDerivation.chapter_id.in_(chapter_ids)).all() if chapter_ids else []
    formulas = PhysicsFormula.query.filter(PhysicsFormula.chapter_id.in_(chapter_ids)).all() if chapter_ids else []

    total_derivations = len(derivations)
    completed_derivations = sum(1 for d in derivations if d.proof_completed)

    return render_template('subjects/physics_hub.html',
                           subject=subject,
                           chapters=chapters,
                           derivations=derivations,
                           formulas=formulas,
                           total_derivations=total_derivations,
                           completed_derivations=completed_derivations)

@physics_bp.route('/derivation/add', methods=['POST'])
@login_required
def add_derivation():
    chapter_id = request.form.get('chapter_id')
    name = request.form.get('name').strip()
    statement = request.form.get('statement').strip()
    importance = int(request.form.get('importance_rating', 3))

    if not chapter_id or not name or not statement:
        flash('Derivation name, chapter, and statement are required.', 'danger')
        return redirect(url_for('physics.hub'))

    derivation = PhysicsDerivation(
        chapter_id=chapter_id,
        name=name,
        statement=statement,
        importance_rating=importance
    )
    db.session.add(derivation)
    db.session.commit()
    flash('Physics derivation logged successfully!', 'success')
    return redirect(url_for('physics.hub'))

@physics_bp.route('/derivation/toggle/<int:derivation_id>', methods=['POST'])
@login_required
def toggle_derivation(derivation_id):
    derivation = PhysicsDerivation.query.get_or_404(derivation_id)
    derivation.proof_completed = not derivation.proof_completed
    db.session.commit()
    return redirect(url_for('physics.hub'))