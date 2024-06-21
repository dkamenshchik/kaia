from unittest import TestCase
from datetime import datetime, timedelta, time
from kaia.eaglesong.core import Automaton, Scenario, TimerTick
from kaia.kaia.skills import KaiaTestAssistant, TimeSkill, DateSkill, ByTheWayIntentTrigger, ByTheWaySkill, ByTheWayNotification
from kaia.infra import ScheduledTime
from kaia.avatar.dub.core import Utterance, Template
from kaia.kaia.skills.time import TimeIntents
from kaia.kaia.skills.date import DateIntents
from kaia.kaia.core import DateTimeTestFactory

ut = Template('By the way, test').utter()

def get_scenario(*notification: ByTheWayNotification):
    factory = DateTimeTestFactory()
    btw = ByTheWaySkill(notification, factory)
    assistant = KaiaTestAssistant(
        [
            TimeSkill(),
            DateSkill(),
            btw
        ]
    )
    assistant.datetime_factory = factory
    btw.assistant = assistant

    sc = Scenario(lambda: Automaton(assistant, None))
    return sc, factory



class ByTheWayTestCase(TestCase):
    def test_basic(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (ByTheWayIntentTrigger((TimeIntents.question,), 0),),
            ut,
            24
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check(ut.assertion)
            .validate()
        )

    def test_runs_after_proper_intent(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (ByTheWayIntentTrigger((TimeIntents.question,), 0),),
            ut,
            24
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(DateIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check()
            .validate()
        )

    def test_respects_delay(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (ByTheWayIntentTrigger((TimeIntents.question,), 60),),
            ut,
            24
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check()
            .act(lambda: factory.add(59))
            .send(TimerTick())
            .check()
            .act(lambda: factory.add(1))
            .send(TimerTick())
            .check(ut.assertion)
            .validate()
        )

    def test_without_cooldown(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (ByTheWayIntentTrigger((TimeIntents.question,), 0),),
            ut,
            0
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check(ut.assertion)
            .act(lambda: factory.add(1))
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check(ut.assertion)
            .validate()
        )

    def test_respects_cooldown(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (ByTheWayIntentTrigger((TimeIntents.question,), 0),),
            ut,
            1
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check(ut.assertion)
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check()
            .act(lambda: factory.add(60*60*1))
            .send(TimeIntents.question.utter())
            .check(Utterance)
            .send(TimerTick())
            .check(ut.assertion)
            .validate()
        )

    def test_multiple_triggers(self):
        notification = ByTheWayNotification(
            ScheduledTime(time(0, 0, 0), timedelta(hours=24)),
            (
                ByTheWayIntentTrigger((TimeIntents.question,), 5),
                ByTheWayIntentTrigger((DateIntents.question,), 12)
            ),
            ut,
            0
        )
        sc, factory = get_scenario(notification)
        (
            sc
            .send(TimeIntents.question.utter())
            .act(lambda: factory.add(4))
            .act(lambda: print('AFTER TIME INTENTS'))
            .send(TimerTick())
            .check()
            .send(DateIntents.question.utter())
            .act(lambda: factory.add(2))
            .act(lambda: print('AFTER DATE INTENTS'))
            .send(TimerTick())
            .check() #Because second intent should have overriden the first
            .act(lambda: factory.add(12))
            .send(TimerTick())
            .check(ut.assertion)
            .validate()
        )



