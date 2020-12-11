from commands import icommand
import time
from common.log import botlogger as LOGGER
from common.utils import constants as CONTS

logger = LOGGER.get_logger(__name__)

import discord
import pyttsx3


def get_cmd_class():
    return VoiceCmd()


class VoiceCmd(icommand.B6Cmd):
    def __init__(self):
        super(VoiceCmd, self).__init__()
        self.cmd_string_long = "voice"
        self.cmd_string_short = "v"
        self.engine = pyttsx3.init()  # object creation

    async def execute_cmd(self, arg_str, message):

        if arg_str.startswith("-f"):
            audio_file = arg_str.replace("-f", "").strip() + ".mp3"

        else:
            self.engine.save_to_file(arg_str, "test.mp3")
            self.engine.runAndWait()
            self.engine.stop()
            audio_file = "./test.mp3"

        self.engine.setProperty("volume", 1.0)
        voices = self.engine.getProperty("voices")  # getting details of current voice
        self.engine.setProperty("voice", voices[0].id)  # changing index, changes voices

        try:
            voice_con = await message.guild.voice_channels[0].connect()
            voice_con.play(
                discord.FFmpegPCMAudio(executable=CONTS.DIR.FFMPEG, source=audio_file)
            )

            while voice_con.is_playing():
                time.sleep(0.1)
        finally:
            await voice_con.disconnect()
