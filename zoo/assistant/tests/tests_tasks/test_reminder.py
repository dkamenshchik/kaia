import os
import unittest
from datetime import datetime
from zoo.assistant.skills.tasks.reminder.reminder_tracker import ReminderTracker
from zoo.assistant.skills.tasks.reminder.time_provider import TimeProvider
from zoo.assistant.skills.tasks.reminder.reminder import Reminder


class MockTimeProvider(TimeProvider):
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now

    def set_now(self, now):
        self._now = now


class TestReminderList(unittest.TestCase):
    def setUp(self):
        self.time_provider = MockTimeProvider(datetime(2024, 1, 1, 12, 0))
        reminders = [
            Reminder("Test reminder 1", ["12:00", "13:00", "18:00"], [0]),
            Reminder("Test reminder 2", ["13:00", "16:00", "19:00"])
        ]
        self.reminder_tracker = ReminderTracker(reminders, self.time_provider)

    def test_get_reminder_by_exact_time(self):
        self.time_provider.set_now(datetime(2024, 1, 1, 12, 0))
        self.assertEqual("Test reminder 1", self.reminder_tracker.get_reminders())

    def test_get_multiple_reminders_by_exact_time(self):
        self.time_provider.set_now(datetime(2024, 1, 1, 13, 0))
        self.assertEqual(f"Test reminder 1{os.linesep}Test reminder 2", self.reminder_tracker.get_reminders())

    def test_dont_get_reminders_if_not_within_delta(self):
        self.time_provider.set_now(datetime(2024, 1, 1, 15, 54))
        self.assertIsNone(self.reminder_tracker.get_reminders())

    def test_dont_get_reminder_if_it_was_already_retrieved(self):
        self.time_provider.set_now(datetime(2024, 1, 1, 18, 0))
        self.assertIsNotNone(self.reminder_tracker.get_reminders())
        self.assertIsNone(self.reminder_tracker.get_reminders())

    def test_get_reminder_again_after_reset(self):
        self.time_provider.set_now(datetime(2024, 1, 1, 19, 0))
        self.assertEqual("Test reminder 2", self.reminder_tracker.get_reminders())
        self.time_provider.set_now(datetime(2024, 1, 1, 19, 15))
        self.assertIsNone(self.reminder_tracker.get_reminders())
        self.time_provider.set_now(datetime(2024, 1, 1, 12, 0))
        self.assertEqual("Test reminder 1", self.reminder_tracker.get_reminders())

    def test_get_reminder_by_specific_day_of_the_week(self):
        reminders = [
            Reminder("Test reminder 1", ["12:00", "13:00", "18:00"], [0])
        ]

        self.time_provider.set_now(datetime(2024, 1, 1, 12, 0))
        self.reminder_tracker = ReminderTracker(reminders, self.time_provider)
        self.assertEqual("Test reminder 1", self.reminder_tracker.get_reminders())

        self.time_provider.set_now(datetime(2024, 1, 2, 12, 0))
        self.reminder_tracker = ReminderTracker(reminders, self.time_provider)
        self.assertIsNone(self.reminder_tracker.get_reminders())
