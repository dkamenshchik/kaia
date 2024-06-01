import os
from datetime import timedelta

from zoo.assistant.skills.tasks.notion_service import NotionService
from zoo.assistant.skills.tasks.reminder.reminder import Reminder
from zoo.assistant.skills.tasks.reminder.time_provider import TimeProvider


class ReminderTracker:
    def __init__(self, reminders, time_provider):
        self.reminders = reminders
        self.time_provider = time_provider
        self.time_table = self._get_time_table()

    @staticmethod
    def from_file(file_path: str):
        time_provider = TimeProvider()
        reminders = []
        with open(file_path, 'r') as file:
            for line in file:
                reminder = Reminder.from_str(line)
                reminders.append(reminder)
        return ReminderTracker(reminders, time_provider)

    @staticmethod
    def from_notion(notion_service: NotionService, reminders_page_id: str) -> 'ReminderTracker':
        reminders = notion_service.get_reminders(reminders_page_id)
        time_provider = TimeProvider()
        return ReminderTracker(reminders, time_provider)

    def get_reminders(self, delta_minutes: int = 5) -> str | None:
        matched_reminders = []
        used_times = []
        for (time, reminders) in self.time_table.items():
            if self.time_provider.is_time_within_delta(time, delta_minutes):
                matched_reminders.extend(reminders)
                used_times.append(time)
        self._refresh_time_table_if_needed(used_times, delta_minutes)

        messages = [reminder.message for reminder in matched_reminders]
        return os.linesep.join(messages) if messages else None

    def _get_time_table(self):
        time_table = {}
        today_reminders = [reminder for reminder in self.reminders if
                           self.time_provider.now().weekday() in reminder.days]
        for reminder in today_reminders:
            for time in reminder.times:
                if time not in time_table:
                    time_table[time] = [reminder]
                else:
                    time_table[time].append(reminder)
        return time_table

    def _refresh_time_table_if_needed(self, used_times, delta_minutes: int):
        min_time = min([time for reminder in self.reminders for time in reminder.times])
        if self.time_provider.is_time_within_delta(min_time - timedelta(minutes=2 * delta_minutes), delta_minutes):
            self.time_table = self._get_time_table()
        else:
            for time in used_times:
                self.time_table.pop(time)
