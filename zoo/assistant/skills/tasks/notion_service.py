from notion_client import Client as NotionClient
from zoo.assistant.skills.tasks.reminder.reminder import Reminder


class NotionService:
    def __init__(self, token_v2):
        self.client = NotionClient(auth=token_v2)

    def get_reminders(self, reminders_page_id: str) -> list[Reminder]:
        response = self.client.blocks.children.list(reminders_page_id)
        return [Reminder.from_str(reminder_obj['paragraph']['rich_text'][0]['plain_text']) for reminder_obj in
                response['results']]
