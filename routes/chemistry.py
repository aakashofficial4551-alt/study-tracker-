from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.core import Subject, Chapter
from models.chemistry import OrganicReaction, InorganicProperty, ChemistryFormula

chemistry_bp = Blueprint('chemistry', __name__)

@chemistry_bp.route('/')
@chemistry_bp.route('/hub')
@login_required
def hub():
    """Chemistry Subject Hub dashboard for Organic, Inorganic, and Physical Chemistry."""
    subject = Subject.query.filter_by(name='Chemistry').first()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() if subject else []
    
    chapter_ids = [c.id for c in chapters]
    organic_reactions = OrganicReaction.query.filter(OrganicReaction.chapter_id.in_(chapter_ids)).all() if chapter_ids else []
    inorganic_props = InorganicProperty.query.filter(InorganicProperty.chapter_id.in_(chapter_ids)).all() if chapter_ids else []

    named_reactions_count = sum(1 for r in organic_reactions if r.is_named_reaction)
    mechanisms_mastered = sum(1 for r in organic_reactions if r.mechanism_known)

    return render_template('subjects/chemistry_hub.html',
                           subject=subject,
                           chapters=chapters,
                           reactions=organic_reactions,
                           inorganic_props=inorganic_props,
                           named_reactions_count=named_reactions_count,
                           mechanisms_mastered=mechanisms_mastered)

@chemistry_bp.route('/reaction/add', methods=['POST'])
@login_required
def add_reaction():
    chapter_id = request.form.get('chapter_id')
    reaction_name = request.form.get('reaction_name').strip()
    reactants = request.form.get('reactants').strip()
    products = request.form.get('products').strip()
    reagents = request.form.get('reagents').strip()
    is_named = True if request.form.get('is_named_reaction') else False

    if not chapter_id or not reaction_name:
        flash('Reaction name and chapter are required.', 'danger')
        return redirect(url_for('chemistry.hub'))

    reaction = OrganicReaction(
        chapter_id=chapter_id,
        reaction_name=reaction_name,
        reactants=reactants,
        products=products,
        reagents=reagents,
        is_named_reaction=is_named
    )
    db.session.add(reaction)
    db.session.commit()
    flash('Organic reaction saved successfully!', 'success')
    return redirect(url_for('chemistry.hub'))