import csv
import io
import pandas as pd

class ExportEngine:
    """Generates CSV and Excel exports for reports and data analytics."""

    @staticmethod
    def export_sessions_to_csv(sessions):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Subject', 'Duration (Mins)', 'Study Type', 'Accuracy (%)', 'Date'])

        for s in sessions:
            acc = round((s.correct_count / s.questions_solved * 100), 2) if s.questions_solved > 0 else 0.0
            writer.writerow([s.id, s.subject_id, s.actual_study_time_minutes, s.study_type, acc, s.start_time.strftime('%Y-%m-%d')])

        output.seek(0)
        return output.getvalue()