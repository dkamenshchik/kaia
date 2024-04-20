import os
from datetime import datetime, timedelta


class TimeProvider:
    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def time_to_timedelta(time_str: str) -> timedelta:
        h, m = map(int, time_str.split(":"))
        return timedelta(hours=h, minutes=m)

    def is_time_within_delta(self, time: timedelta, delta_minutes: int) -> bool:
        now = self.now()
        now_time = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
        diff = (now_time - time).total_seconds() / 60
        return 0 <= diff <= delta_minutes


class Reminder:
    def __init__(self, message, times, time_provider):
        self.message = message
        self.times = sorted([time_provider.time_to_timedelta(time) for time in times])
        self.checked_times = set()
        self.time_provider = time_provider

    def get_reminder(self, delta_minutes: int = 5) -> str | None:
        if self.time_provider.is_time_within_delta(
                self.times[-1] + timedelta(minutes=2 * delta_minutes),
                delta_minutes):
            self.checked_times.clear()

        for time in self.times:
            if self.time_provider.is_time_within_delta(time, delta_minutes) and time not in self.checked_times:
                self.checked_times.add(time)
                return self.message
        return None


class ReminderList:
    def __init__(self, reminders, time_provider):
        self.reminders = reminders
        self.time_provider = time_provider

    @staticmethod
    def with_presets():
        time_provider = TimeProvider()
        reminders = []
        with open(os.environ["REMINDERS_PATH"], 'r') as file:
            for line in file:
                message, times = line.strip().split(';')
                times = times.split(',')
                reminders.append(Reminder(message, times, time_provider))
        return ReminderList(reminders, time_provider)

    def add_reminder(self, message: str, times: [str]) -> None:
        self.reminders.append(Reminder(message, times, self.time_provider))

    def get_reminders(self, delta_minutes: int = 5) -> str | None:
        messages = [reminder.get_reminder(delta_minutes) for reminder in self.reminders]
        messages = [msg for msg in messages if msg is not None]
        return os.linesep.join(messages) if messages else None
