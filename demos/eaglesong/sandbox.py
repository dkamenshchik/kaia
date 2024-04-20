from demos.eaglesong.common import *
from demos.eaglesong.example_06_auth_4 import Authorize
from kaia.eaglesong.amenities import menu
from kaia.eaglesong.amenities.menu import ValueMenuItem, FunctionalMenuItem, MenuFolder
from zoo.assistant.skills.tasks.reminder import ReminderList
from zoo.assistant.skills.tasks.streak_tracker import StreakTracker, Task


def main():
    reminder = ReminderList.with_presets()
    streak_tracker = StreakTracker([])
    streak_tracker.load_from_file()
    context = yield ContextRequest()
    timer_state = False
    menu_aut = None  # type: Optional[Automaton]
    yield 'This bot will send you reminders. Enter /toggle to pause/resume, or /streak to open streak menu.'
    input = yield Listen()
    while True:
        if isinstance(input, TimerTick):
            if timer_state:
                msg = reminder.get_reminders()
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
    streak_tracker.save_to_file()
    yield f'{task.description} streak is {new_streak}'


def create_menu(streak_tracker: StreakTracker):
    menu_items = [FunctionalMenuItem(
        f'{task.description}: {task.streak}',
        (lambda task_local=task: update_streak(task_local, streak_tracker)),
        True)
        for task in streak_tracker.get_tasks()]

    return MenuFolder('Streak').items(*menu_items)


bot = Bot("timer2", Authorize('KAIA_TEST_BOT_CHAT_ID', main), timer=True, timer_interval=60)

if __name__ == '__main__':
    run(bot)
