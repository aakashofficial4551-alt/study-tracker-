# StudyOS - Premium Class 12 CBSE PCM Management System

StudyOS is a highly advanced, production-ready study management application designed specifically for Class 12 CBSE Science students (Physics, Chemistry, Mathematics, English). 

## Features
- **Intelligent Study Sessions:** Deep work tracking with Focus Mode.
- **Micro-Trackers:** Dedicated tracking for physics derivations, organic reactions, math theorems, and reading speeds.
- **Mistake Notebook & Spaced Repetition:** Automated AI-driven revision scheduling.
- **Lifestyle Tracking:** Gym, sleep, meditation, and water intake logging.
- **Analytics Dashboard:** Real-time Chart.js graphs, GitHub-style heatmaps, and AI grade prediction.

## Installation
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize Database: `flask db init`, `flask db migrate`, `flask db upgrade`
6. Run the application: `python run.py`