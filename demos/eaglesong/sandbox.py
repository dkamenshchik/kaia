from demos.eaglesong.common import *
from demos.eaglesong.example_06_auth_4 import Authorize
from demos.eaglesong.example_08_menu_2 import create_menu
from zoo.assistant.skills.tasks.reminder import ReminderList


def main():
    reminder = ReminderList.with_presets()
    context = yield ContextRequest()
    timer_state = False
    menu_aut = None  # type: Optional[Automaton]
    yield 'This bot will send you reminders. Enter /toggle to pause/resume, or /menu to open menu.'
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

        if input == '/menu':
            menu_aut = Automaton(create_menu(), context)

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


bot = Bot("timer2", Authorize('KAIA_TEST_BOT_CHAT_ID', main), timer=True, timer_interval=60)

if __name__ == '__main__':
    run(bot)
