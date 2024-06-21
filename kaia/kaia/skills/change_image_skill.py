from typing import *
from kaia.eaglesong.core import Image
from kaia.avatar.dub.languages.en import *
from kaia.kaia.core import SingleLineKaiaSkill
from kaia.avatar.server import AvatarAPI


class ChangeImageIntents(TemplatesCollection):
    change_image = Template("Change image")
    bad_image = Template("Bad image")
    hide_image = Template("Hide image")
    good_image = Template('Good image')

class ChangeImageReplies(TemplatesCollection):
    answer = Template("Here is a new image for you")
    thanks = Template("Thanks, I'm flattered! You're cute too!")





class ChangeImageSkill(SingleLineKaiaSkill):
    def __init__(self, avatar_api: AvatarAPI):
        super().__init__(ChangeImageIntents, ChangeImageReplies)
        self.avatar_api = avatar_api
        self.last_image: Optional[Image] = None



    def run(self):
        input: Utterance = yield
        if input.template.name == ChangeImageIntents.change_image.name:
            yield self.avatar_api.image_get()
        elif input.template.name == ChangeImageIntents.bad_image.name:
            self.avatar_api.image_report('bad')
            yield self.avatar_api.image_get()
        elif input.template.name == ChangeImageIntents.hide_image.name:
            yield self.avatar_api.empty_image()
        if input.template.name == ChangeImageIntents.good_image.name:
            self.avatar_api.image_report('good')
            yield ChangeImageReplies.thanks.utter()




