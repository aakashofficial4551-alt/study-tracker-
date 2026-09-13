from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.core import Subject, Chapter
from models.english import EnglishChapter, EnglishVocabulary, EnglishWritingPractice

english_bp = Blueprint('english', __name__)

@english_bp.route('/')
@english_bp.route('/hub')
@login_required
def hub():
    """English Literature, Writing Skills, and Vocabulary Hub."""
    subject = Subject.query.filter_by(name='English').first()
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() if subject else []

    vocab_words = EnglishVocabulary.query.order_by(EnglishVocabulary.id.desc()).limit(20).all()
    writing_practices = EnglishWritingPractice.query.order_by(EnglishWritingPractice.id.desc()).all()

    return render_template('subjects/english_hub.html',
                           subject=subject,
                           chapters=chapters,
                           vocab_words=vocab_words,
                           writing_practices=writing_practices)

@english_bp.route('/vocab/add', methods=['POST'])
@login_required
def add_vocab():
    word = request.form.get('word').strip()
    meaning = request.form.get('meaning').strip()
    synonyms = request.form.get('synonyms', '').strip()
    example = request.form.get('example', '').strip()

    if not word or not meaning:
        flash('Word and meaning are required.', 'danger')
        return redirect(url_for('english.hub'))

    vocab = EnglishVocabulary(
        word=word,
        meaning=meaning,
        synonyms=synonyms,
        example_sentence=example
    )
    db.session.add(vocab)
    db.session.commit()
    flash(f'Added "{word}" to your English vocabulary bank!', 'success')
    return redirect(url_for('english.hub'))