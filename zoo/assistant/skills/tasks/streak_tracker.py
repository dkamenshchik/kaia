import csv
import datetime
from typing import List

from zoo.assistant.skills.tasks.notion_service import NotionService
from zoo.assistant.skills.tasks.task import Task


class StreakTracker:
    def __init__(self, tasks: List[Task]):
        self.tasks = {task.id: task for task in tasks}

    def get_tasks(self) -> [Task]:
        return list(self.tasks.values())

    def recalculate_streak(self, task_id: int) -> int:
        if task_id in self.tasks:
            new_task = self.tasks[task_id].add_date(datetime.date.today())
            self.tasks[task_id] = new_task
            return new_task.streak

    def save(self) -> None:
        pass


class NotionStreakTracker(StreakTracker):
    def __init__(self, tasks: List[Task], notion_service: NotionService, streaks_page_id: str):
        super().__init__(tasks)
        self.notion_service = notion_service
        self.streaks_page_id = streaks_page_id

    def save(self) -> None:
        self.save_to_notion()

    def save_to_notion(self) -> None:
        self.notion_service.save_streaks(self.streaks_page_id, self.get_tasks())

    @staticmethod
    def from_notion(notion_service: NotionService, streaks_page_id: str) -> 'StreakTracker':
        tasks = notion_service.get_streaks(streaks_page_id)
        return NotionStreakTracker(tasks, notion_service, streaks_page_id)


class FileStreakTracker(StreakTracker):
    def __init__(self, tasks: List[Task], filename: str):
        super().__init__(tasks)
        self.filename = filename

    @staticmethod
    def from_file(filename: str) -> 'StreakTracker':
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            tasks = [Task.from_str(','.join(row)) for row in reader]
            return FileStreakTracker(tasks, filename)

    def save(self) -> None:
        self.save_to_file()

    def save_to_file(self) -> None:
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'description', 'dates'])
            for task in self.get_tasks():
                writer.writerow([task.id, task.description, ';'.join(map(str, task.dates))])
