import os as os1

from demos.eaglesong.common import *
from demos.eaglesong.example_06_auth_4 import Authorize
from kaia.eaglesong.amenities.menu import FunctionalMenuItem, MenuFolder
from zoo.assistant.skills.tasks.notion_service import NotionService
from zoo.assistant.skills.tasks.reminder.reminder_tracker import ReminderTracker
from zoo.assistant.skills.tasks.streak_tracker import StreakTracker, FileStreakTracker, NotionStreakTracker


def main():
    context = yield ContextRequest()
    reminder_tracker = get_reminder_tracker(context.user_id)
    streak_tracker = get_streak_tracker(context.user_id)
    timer_state = False
    menu_aut = None  # type: Optional[Automaton]
    yield 'This bot will send you reminders. Enter /toggle to pause/resume, or /streak to open streak menu.'
    input = yield Listen()
    while True:
        if isinstance(input, TimerTick):
            if timer_state:
                msg = reminder_tracker.get_reminders()
                if msg is not None:
                    yield msg
            input = yield Listen()
            continue
        if input == '/toggle':
            timer_state = not timer_state
            yield 'Timer set to ' + str(timer_state)
            input = yield Listen()
            continue

        if input == '/streak':
            menu_aut = Automaton(create_menu(streak_tracker), context)

        if menu_aut is not None:
            result = menu_aut.process(input)
            if isinstance(result, AutomatonExit):
                menu_aut = None
                input = yield Listen()
            else:
                input = yield result
            continue

        yield f'Unexpected input: {input}'
        input = yield Listen()


def update_streak(task, streak_tracker: StreakTracker):
    new_streak = streak_tracker.recalculate_streak(task.id)
    yield f'{task.description} streak is {new_streak}'
    streak_tracker.save()


def create_menu(streak_tracker: StreakTracker):
    menu_items = [FunctionalMenuItem(
        f'{task.description}: {task.streak}',
        (lambda task_local=task: update_streak(task_local, streak_tracker)),
        True)
        for task in streak_tracker.get_tasks()]
    menu_items.append(FunctionalMenuItem(
        'Print streaks',
        lambda: (yield os.linesep.join([f'{task.description}: {task.streak} {("✔️" if task.is_done_today() else "")}'
                                        for task in streak_tracker.get_tasks()])),
        True))

    return MenuFolder('Streak').items(*menu_items)


def get_reminder_tracker(user_id: str) -> ReminderTracker:
    notion_token = os.environ.get(f"NOTION_TOKEN_{user_id}")
    if notion_token:
        notion_service = NotionService(notion_token)
        return ReminderTracker.from_notion(
            notion_service,
            os.environ.get(f"NOTION_REMINDERS_PAGE_ID_{user_id}"))

    return ReminderTracker.from_file(f"{os.environ.get('REMINDERS_PATH')}_{user_id}.csv")


def get_streak_tracker(user_id: str) -> StreakTracker:
    notion_token = os.environ.get(f"NOTION_TOKEN_{user_id}")
    if notion_token:
        notion_service = NotionService(notion_token)
        return NotionStreakTracker.from_notion(
            notion_service,
            os.environ.get(f"NOTION_STREAKS_PAGE_ID_{user_id}")
        )

    return FileStreakTracker.from_file(f"{os.environ.get('STREAK_TRACKER_PATH')}_{user_id}.csv")


bot = Bot("timer2", Authorize('KAIA_TEST_BOT_CHAT_ID', main), timer=True, timer_interval=60)

if __name__ == '__main__':
    run(bot)
