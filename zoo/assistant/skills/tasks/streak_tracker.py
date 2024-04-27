import csv
import datetime
import os
from typing import List


class Task:
    def __init__(self, id: int, description: str, dates: List[datetime.date]):
        self.id = id
        self.description = description
        self.dates = list(set(dates))
        self.streak = self.calculate_streak()

    def calculate_streak(self):
        self.dates.sort()
        if len(self.dates) <= 1:
            return len(self.dates)
        streak = 1
        for date1, date2 in zip(self.dates, self.dates[1:]):
            if date2 - date1 == datetime.timedelta(days=1):
                streak += 1
            else:
                streak = 1
        return streak

    def add_date(self, date: datetime.date):
        new_dates = self.dates + [date]
        return Task(self.id, self.description, new_dates)


class StreakTracker:
    def __init__(self, tasks: List[Task]):
        self.tasks = {task.id: task for task in tasks}

    def get_tasks(self) -> [Task]:
        return list(self.tasks.values())

    def recalculate_streak(self, task_id: int):
        if task_id in self.tasks:
            new_task = self.tasks[task_id].add_date(datetime.date.today())
            self.tasks[task_id] = new_task
            return new_task.streak

    def save_to_file(self, filename: str):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'description', 'dates'])
            for task in self.get_tasks():
                writer.writerow([task.id, task.description, ';'.join(map(str, task.dates))])

    def load_from_file(self, filename: str):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            self.tasks = {
                int(row[0]): Task(
                    int(row[0]),
                    row[1],
                    [] if not row[2] else list(map(datetime.date.fromisoformat, filter(None, row[2].split(';'))))
                )
                for row in reader}
