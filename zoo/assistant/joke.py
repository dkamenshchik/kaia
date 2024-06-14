import requests
from kaia.avatar.dub.languages.en import *
from kaia.kaia.core import SingleLineKaiaSkill


class JokeIntents(TemplatesCollection):
    tell_a_joke = Template('Tell a joke')


class JokeSkill(SingleLineKaiaSkill):
    def __init__(self):
        super().__init__(JokeIntents)

    def run(self):
        reply = requests.get('https://v2.jokeapi.dev/joke/Any?type=single')
        yield reply.json()['joke']



