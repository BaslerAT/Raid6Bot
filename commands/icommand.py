class R6Cmd:
    def __init__(self):
        self.cmd_string_long = ""
        self.cmd_string_short = ""

    def is_cmd(self, cmd_str):
        return cmd_str in (self.cmd_string_long, self.cmd_string_short)

    def execute_cmd(arg_str):
        pass