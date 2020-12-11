# bot.py
import random
import json
import queue

from common.utils import commands as CMDUTIL
import common.utils.util as UTILS
from common.utils import config as CONFIG
from common.log import botlogger as LOGGER
from common.utils import constants as CONTS
import time

logger = LOGGER.get_logger(__name__)

# 1
import discord


class BOTtomBitchClient(discord.Client):
    def __init__(self):
        """
        constructor/init
        """
        # List of registered commands
        self.cmd_classes = []

        self.cmd_q = queue.Queue()

        # self.cmd_q_thread = threading.Thread(target=await self.process_cmd_q)
        # self.cmd_q_thread.start()

        self.stopped = False

        # call super init
        super(BOTtomBitchClient, self).__init__()

        # load the config file into a json dict
        self.config = CONFIG.get_instance()
        self.config.load_config()

        # parse that dict into self values
        self.parse_config()

        self.cmd_classes += CMDUTIL.load_commands()
        self.cmd_classes += CMDUTIL.load_commands("../common/commands")

        UTILS.set_client(self)

    def parse_config(self):
        """
        parse config dict into specific self vars
        """
        self.token = self.config.get_attr("DISCORD_TOKEN")
        self.cmd_prefix = self.config.get_attr("CMD_PREFIX")

    async def on_ready(self):
        """
        on connect to discord server
        """
        for guild in self.guilds:
            logger.debug(
                f"{self.user} is connected to the following guild:\n"
                f"{guild.name}(id: {guild.id})"
            )

    async def on_voice_state_update(self, member, before, after):
        intro_audio = None

        intro_settings = self.config.get_attr(CONTS.CONFIG.INTRO)

        intros = {
            "CommonCommentary": "./intro.mp3",
            "jfly": "./jbuttsintro.mp3",
            "Swarley Hats": "./swarley.mp3",
            "Poe": "./fpoe.mp3",
        }

        if (
            before.channel is None
            and after.channel.name == "General"
            and member.display_name in intros
            and (
                (
                    member.display_name not in intro_settings
                    and intro_settings["Default"]
                )
                or (
                    member.display_name in intro_settings
                    and intro_settings[member.display_name]
                )
            )
        ):

            intro_audio = intros[member.display_name]

        if intro_audio is not None:
            try:
                voice_con = await after.channel.connect()
                voice_con.play(
                    discord.FFmpegPCMAudio(
                        executable=CONTS.DIR.FFMPEG, source=intro_audio
                    )
                )

                while voice_con.is_playing():
                    time.sleep(2)
            finally:
                await voice_con.disconnect()

    async def on_message(self, message):
        """
        when a message is sent
        """
        # if the author of the message is the bot user
        if message.author == self.user:
            # don't respond, because it's yourself
            return

        # If the message content contains one of the died trigger phrase
        if (
            "I died" in message.content
            or "i died" in message.content
            or "killed me" in message.content
        ):
            # open the death responses file
            with open("./death_responses.json", "r") as responses_file:
                # load the death response file into a json dict
                responses = json.load(responses_file)

            # send a random response
            await message.channel.send(random.choice(responses))

        # Message Commands
        # If the message doesn't start with the command prefix
        if not (message.content.startswith(self.cmd_prefix)):
            # do nothing
            return

        # Else it has command prefix
        # chop it off
        full_cmd_str = message.content[len(self.cmd_prefix) :].strip()

        # get the specific command word
        cmd_str = full_cmd_str.split()[0]

        # the rest of the wprds must be arguments
        arg_str = full_cmd_str[len(cmd_str) :].strip()

        # log command
        logger.debug(f"cmd:{cmd_str}")

        # for each of the registered commands
        for cmd_class in self.cmd_classes:
            # use command class method to test if this is the correct cmd
            if cmd_class.is_cmd(cmd_str=cmd_str):
                # found class
                logger.debug(
                    f"Found cmd class: {cmd_class.__class__} for cmd: {cmd_str}"
                )
                try:
                    # execute command
                    await cmd_class.execute_cmd(arg_str, message)
                except Exception as e:
                    logger.error(f"Exception when executing command!\n{e}")
                    await UTILS.fail_reaction(message=message)
                    raise e
                break

        await UTILS.confirm_message_cmd(message)

    async def on_member_join(self, member):
        pass

    async def process_cmd_q(self):
        while not self.stopped:
            cmd_func = self.cmd_q.get()

            await cmd_func()


if __name__ == "__main__":
    botty_client = BOTtomBitchClient()
    botty_client.run(botty_client.token)
