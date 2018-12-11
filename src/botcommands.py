from enum import Enum, unique


@unique
class BotCommands(Enum):
    SHOW_TASK = '!show_task'
    REGME = '!regme'
    EXEC = '!exec'
    VALIDATE = '!validate'
    DISCARD = '!discard'
    PROFILE = '!profile'
    INV = '!inv'
    SHOW_STACK = '!show_stack'
    HELP = '!help'
    GET_MAX_POINTS = '!get_max_points'
    CHANGE_LANG = '!change_lang'
    GET_CURRENT_PHASE = '!get_current_phase'  # TODO: not realized
    START_PHASE = '!start_phase'
    START_SCENARIO = '!start_scenario'  # TODO: not realized
    ADD_ITEM = '!add_item'
    REMOVE_ITEM = '!remove_item'
    GET_ITEM_INFO = '!get_item_info'
