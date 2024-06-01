from zoo.assistant.skills.tasks.reminder.time_provider import TimeProvider


class Reminder:
    _whole_week = [0, 1, 2, 3, 4, 5, 6]

    def __init__(self, message, times, days=None):
        self.message = message
        self.times = [TimeProvider.time_to_timedelta(time) for time in times]
        self.days = days or self._whole_week

    @staticmethod
    def from_str(line: str) -> 'Reminder':
        message, times, days = line.strip().split(';')
        times = times.split(',')
        days = [int(day) for day in days.split(',')] if days else None
        reminder = Reminder(message, times, days)
        return reminder
