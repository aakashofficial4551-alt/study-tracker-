from datetime import datetime, timedelta

class SpacedRepetitionEngine:
    """
    Implementation of the SuperMemo-2 (SM-2) algorithm for revision scheduling.
    Default intervals: 1, 3, 7, 15, 30, 60, 90, 180, 365 days.
    """
    INTERVALS = [1, 3, 7, 15, 30, 60, 90, 180, 365]

    @classmethod
    def get_next_revision_date(cls, current_interval_days):
        try:
            current_index = cls.INTERVALS.index(current_interval_days)
            next_index = min(current_index + 1, len(cls.INTERVALS) - 1)
            next_interval = cls.INTERVALS[next_index]
        except ValueError:
            next_interval = 1

        next_date = datetime.utcnow().date() + timedelta(days=next_interval)
        return next_interval, next_date