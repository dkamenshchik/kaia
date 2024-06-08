import datetime
from typing import List


class Task:
    def __init__(self, id: int, description: str, dates: List[datetime.date]):
        self.id = id
        self.description = description
        self.dates = list(set(dates))
        self.streak = self.calculate_streak()

    def calculate_streak(self) -> int:
        self.dates.sort()
        if len(self.dates) <= 1:
            return len(self.dates)
        streak = 1
        for date1, date2 in zip(self.dates, self.dates[1:]):
            if date2 - date1 <= datetime.timedelta(days=2):
                streak += 1
            else:
                streak = 1
        return streak

    def add_date(self, date: datetime.date) -> 'Task':
        new_dates = self.dates + [date]
        return Task(self.id, self.description, new_dates)

    def is_done_today(self) -> bool:
        return datetime.date.today() in self.dates

    @staticmethod
    def from_str(line: str) -> 'Task':
        task_id, description, dates = line.strip().split(',')
        dates = [] if not dates else list(map(datetime.date.fromisoformat, filter(None, dates.split(';'))))
        return Task(int(task_id), description, dates)

    def to_csv_str(self):
        return f'{self.id},{self.description},{";".join(map(str, self.dates))}'
