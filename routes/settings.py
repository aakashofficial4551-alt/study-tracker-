from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from extensions import db
import os

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def settings_page():
    if request.method == 'POST':
        current_user.daily_study_goal_hours = float(request.form.get('daily_study_goal', 6.0))
        current_user.target_board_score = float(request.form.get('target_board_score', 95.0))
        current_user.theme = request.form.get('theme', 'dark')
        current_user.accent_color = request.form.get('accent_color', '#3b82f6')

        db.session.commit()
        flash('Preferences and target goals updated successfully!', 'success')
        return redirect(url_for('settings.settings_page'))

    return render_template('settings/settings.html', user=current_user)

@settings_bp.route('/backup/download')
@login_required
def download_backup():
    """Allows downloading the SQLite database file as a manual backup."""
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../studyos_production.db')
    if os.path.exists(db_path):
        return send_file(db_path, as_attachment=True, download_name='studyos_backup.db')
    flash('Database file not found.', 'danger')
    return redirect(url_for('settings.settings_page'))