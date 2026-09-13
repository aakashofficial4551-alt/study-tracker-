from extensions import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # Physics, Chemistry, Mathematics, English
    code = db.Column(db.String(10), nullable=False)
    total_chapters = db.Column(db.Integer, default=0)

    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='Not Started') # Not Started, In Progress, Completed, Under Revision
    
    date_started = db.Column(db.Date, nullable=True)
    date_completed = db.Column(db.Date, nullable=True)
    completion_percentage = db.Column(db.Float, default=0.0)
    
    estimated_study_hours = db.Column(db.Float, default=10.0)
    actual_study_hours = db.Column(db.Float, default=0.0)
    revision_count = db.Column(db.Integer, default=0)
    confidence_percentage = db.Column(db.Float, default=0.0)
    
    # CBSE Board Exam Expectations
    expected_marks = db.Column(db.Float, default=0.0)
    actual_marks = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.Text, nullable=True)

    # General NCERT & Prep Checklists
    ncert_completed = db.Column(db.Boolean, default=False)
    ncert_examples_completed = db.Column(db.Boolean, default=False)
    ncert_exercise_completed = db.Column(db.Boolean, default=False)
    exemplar_completed = db.Column(db.Boolean, default=False)
    pyq_completed = db.Column(db.Boolean, default=False)
    own_notes_completed = db.Column(db.Boolean, default=False)
    formula_sheet_completed = db.Column(db.Boolean, default=False)

    topics = db.relationship('Topic', backref='chapter', lazy=True, cascade="all, delete-orphan")

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='Not Started')
    confidence = db.Column(db.Float, default=0.0)
    is_weak = db.Column(db.Boolean, default=False)
    is_strong = db.Column(db.Boolean, default=False)