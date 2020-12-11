from commands import icommand

from common.log import botlogger as LOGGER
from common.utils import config as CONFIG

logger = LOGGER.get_logger(__name__)


def get_cmd_class():
    return SetIntroCmd()


class SetIntroCmd(icommand.R6Cmd):
    def __init__(self):
        super(SetIntroCmd, self).__init__()
        self.cmd_string_long = "intro"
        self.cmd_string_short = "i"

        self.config = CONFIG.get_instance()

    async def execute_cmd(self, arg_str, message):
        if arg_str.strip().lower() in ("true", "on", "set"):
            intro = True

        elif arg_str.strip().lower() in ("false", "off", "unset"):
            intro = False

        else:
            return

        user = message.author.display_name
        intro_settings = self.config.get_attr(attr="INTRO")
        intro_settings[user] = intro

        self.config.set_attr(attr="INTRO", value=intro_settings, save=True)
