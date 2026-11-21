from extensions import db
from models.subject import Subject


class SyllabusChapter(db.Model):
    __tablename__ = "syllabus_chapters"

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False, index=True)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)


CBSE_SYLLABUS = [
    {
        "name": "Physics",
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
        "name": "Chemistry",
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
        "name": "Mathematics",
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

THEORY_MARKS_MAP = {item["name"]: item["theory_marks"] for item in CBSE_SYLLABUS}


def seed_cbse_syllabus():
    changed = False

    for subj in CBSE_SYLLABUS:
        existing_subj = Subject.query.filter_by(name=subj["name"]).first()
        if not existing_subj:
            db.session.add(
                Subject(
                    name=subj["name"],
                    icon="",
                    color=subj["color"],
                    total_chapters=len(subj["chapters"]),
                )
            )
            changed = True
        elif existing_subj.total_chapters != len(subj["chapters"]):
            existing_subj.total_chapters = len(subj["chapters"])
            changed = True

        existing_count = SyllabusChapter.query.filter_by(
            subject_name=subj["name"]
        ).count()
        if existing_count == 0:
            for idx, title in enumerate(subj["chapters"], start=1):
                db.session.add(
                    SyllabusChapter(
                        subject_name=subj["name"],
                        chapter_number=idx,
                        title=title,
                        completed=False,
                    )
                )
            changed = True

    if changed:
        db.session.commit()
