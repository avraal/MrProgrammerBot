from enum import Enum, unique


@unique
class BotCommands(Enum):
    SHOW_TASK = '!show_task'
    REGME = '!regme'
    EXEC = '!exec'
    VALIDATE = '!validate'
    PROFILE = '!profile'
    SHOW_STACK = '!show_stack'
    HELP = '!help'
