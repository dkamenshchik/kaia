from notion_client import Client as NotionClient
from zoo.assistant.skills.tasks.reminder.reminder import Reminder
from zoo.assistant.skills.tasks.task import Task


class NotionService:
    def __init__(self, token_v2):
        self.client = NotionClient(auth=token_v2)

    def get_reminders(self, reminders_page_id: str) -> list[Reminder]:
        response = self.client.blocks.children.list(reminders_page_id)
        return [Reminder.from_str(reminder_obj['paragraph']['rich_text'][0]['plain_text']) for reminder_obj in
                response['results']]

    def get_streaks(self, streaks_page_id: str) -> list[Task]:
        response = self.client.blocks.children.list(streaks_page_id)
        return [Task.from_str(streak_obj['paragraph']['rich_text'][0]['plain_text']) for streak_obj in
                response['results']]

    def save_streaks(self, streaks_page_id: str, tasks: list[Task]) -> None:
        response = self.client.blocks.children.list(streaks_page_id)
        for block in response['results']:
            self.client.blocks.delete(block['id'])
        for task in tasks:
            self.client.blocks.children.append(
                streaks_page_id,
                children=[NotionObjects.paragraph(task.to_csv_str())])


class NotionObjects:
    @staticmethod
    def paragraph(text: str) -> dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": text
                        }
                    }
                ]
            }
        }
    # Compare this snippet from zoo/assistant/skills/tasks/notion_service.py:
