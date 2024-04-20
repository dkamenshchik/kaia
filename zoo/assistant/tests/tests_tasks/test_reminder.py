import os
import unittest
from datetime import datetime

from zoo.assistant.skills.tasks.reminder import TimeProvider, Reminder, ReminderList


class MockTimeProvider(TimeProvider):
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now

    def set_now(self, now):
        self._now = now


class TestReminder(unittest.TestCase):
    def setUp(self):
        self.time_provider = MockTimeProvider(datetime(2022, 1, 1, 12, 0))
        self.reminder = Reminder("Test Reminder", ["12:00", "15:00", "18:00"], self.time_provider)

    def test_get_reminder(self):
        self.time_provider.set_now(datetime(2022, 1, 1, 12, 0))
        self.assertEqual(self.reminder.get_reminder(), "Test Reminder")
        self.assertIsNone(self.reminder.get_reminder())

        self.time_provider.set_now(datetime(2022, 1, 1, 15, 5))
        self.assertEqual(self.reminder.get_reminder(), "Test Reminder")

        self.time_provider.set_now(datetime(2022, 1, 1, 17, 54))
        self.assertIsNone(self.reminder.get_reminder())

        self.time_provider.set_now(datetime(2022, 1, 1, 18, 6))
        self.assertIsNone(self.reminder.get_reminder())

    def test_get_reminder_with_reset(self):
        self.time_provider.set_now(datetime(2022, 1, 1, 18, 5))
        self.assertEqual(self.reminder.get_reminder(), "Test Reminder")
        self.assertIsNone(self.reminder.get_reminder())

        self.time_provider.set_now(datetime(2022, 1, 1, 18, 6))
        self.assertIsNone(self.reminder.get_reminder())

        self.time_provider.set_now(datetime(2022, 1, 1, 12, 0))
        self.assertEqual(self.reminder.get_reminder(), "Test Reminder")


class TestReminderList(unittest.TestCase):
    def setUp(self):
        self.time_provider = MockTimeProvider(datetime(2022, 1, 1, 12, 0))
        self.reminder_list = ReminderList([], self.time_provider)
        self.reminder_list.add_reminder("Test Reminder 1", ["12:00", "13:00", "18:00"])
        self.reminder_list.add_reminder("Test Reminder 2", ["13:00", "16:00", "19:00"])

    def test_get_reminders(self):
        self.time_provider.set_now(datetime(2022, 1, 1, 12, 0))
        self.assertEqual(self.reminder_list.get_reminders(), "Test Reminder 1")

        self.time_provider.set_now(datetime(2022, 1, 1, 13, 0))
        self.assertEqual(self.reminder_list.get_reminders(), f"Test Reminder 1{os.linesep}Test Reminder 2")

        self.time_provider.set_now(datetime(2022, 1, 1, 11, 54))
        self.assertIsNone(self.reminder_list.get_reminders())
