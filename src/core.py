import discord
import re
import requests
import sys

sys.path.append('../')
from src import keys
from src.botcommands import BotCommands
from enum import Enum, unique


@unique
class Achievements(Enum):
    GET_2TIER = 1,
    FIRST_VOICE_EXPERIENCE = 2,
    TORTURE = 3,
    HELP = 4


@unique
class Languages(Enum):
    CPP = 'C++'
    CS = 'C#'
    WEB = 'Web'

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


client = discord.Client()


def get_task_by_name(name):
    data = requests.post(keys.__get_all_tasks_url__, data={'pr_t_name': name})
    return data.json()['task'][0]


def get_achs(d_id):
    data = requests.post(keys.__get_ach_list_url__, data={'d_id': d_id})
    print(data.content)
    data = data.json()
    msg = ''
    code = data['code']
    if code == 0:
        msg = 'Пользователь не найден'
    elif code == 2:
        msg = 'Достижений нет'
    elif code == 1:
        msg = '```css\n'
        achs = data['ach']
        for a in achs:
            msg += '[' + a['title'] + ']\n'
        msg += '```'
    return msg


def get_inv(d_id):
    data = requests.post(keys.__get_inventory_url__, data={'d_id': d_id})
    msg = ''
    code = data.json()['code']
    if code == 0:
        msg = 'Пользователь не найден'
    elif code == 2:
        msg = 'Инвентарь пуст'
    elif code == 1:
        msg = '```'
        items = data.json()['item']
        for i in items:
            msg += i['pr_i_title']
            if i['pr_i_can_stack'] == '1':
                msg += ' (' + i['i_count'] + ') шт.'
            msg += '\n'
        msg += '```'
    return msg


def parse_task(task):
    task = task.replace('<br>', '\n')
    task = task.replace('<pre>', '')
    task = task.replace('</pre>', '')
    return task


def task_format(json):
    task = {'Name': json['pr_t_name'], 'Text': json['pr_t_text'], 'Points': json['pr_t_points']}
    return task


def reg(author_id, author_class):
    for l in Languages:
        if author_class == l.value:
            break
        else:
            return 3
    data = requests.post(keys.__reg_url__, data={'user_id': author_id, 'author_class': author_class})
    return data.json()['code']


def push_task(discord_id, t_name, t_link):
    data = requests.post(keys.__push_task_url__, data={'discord_id': discord_id, 't_name': t_name, 't_link': t_link})
    return data.json()['code']


def get_max_points():
    data = requests.post(keys.__get_max_points_url__)
    return data.json()['points']


def discard(id_in_stack):
    data = requests.post(keys.__discard_url__, data={'id_in_stack': id_in_stack})
    return data.json()


def validate(id_in_stack):
    data = requests.post(keys.__validate_url__, data={'id_in_stack': id_in_stack})
    return data.json()


def remove_item(d_id, i_id, count):
    data = requests.post(keys.__remove_item_url__, data={'d_id': d_id, 'i_id': i_id, 'count': count})
    data = data.json()
    msg = ''
    if data['code'] == 2:
        msg = 'Кто-то пытался украсть у вас ' + data['i_name']
        if data['i_can_stack'] == '1' and int(data['i_count']) > 1:
            msg += ' в количестве ' + data['i_count'] + ' шт.'
    elif data['code'] == 1:
        msg = 'Предмет ' + data['i_name'] + ' был удалён из вашего инвентаря'
        if data['i_can_stack'] == '1' and int(data['i_count']) > 1:
            msg += ' в количестве ' + data['i_count'] + ' шт.'
    elif data['code'] == 3:
        msg = 'Вы потеряли ' + str(data['i_count']) + ' штук предмета ' + data['i_name']
    return msg


def add_item(d_id, i_id, count):
    data = requests.post(keys.__add_item_url__, data={'d_id': d_id, 'i_id': i_id, 'count': count})
    print(data.content)
    data = data.json()
    msg = ''
    if data:
        code = data['code']
        if code == 0:
            msg = 'Предмет не найден'
        elif code == 2:
            msg = 'Пользователь не найден'
        elif code == 3:
            msg = 'Ошибка запроса'
        elif code == 4:
            msg = 'Вы получили ' + data['item_name']
        elif code == 5:
            msg = 'Количество ' + data['item_name'] + ' увеличено на ' + str(data['count'])
        elif code == 6:
            msg = 'У вас уже есть этот предмет'
    return msg


def change_lang(lang, d_id):
    data = requests.post(keys.__change_lang_url__, data={'lang': lang, 'd_id': d_id})
    return data.json()['code']


def get_user_info(discord_id, param):
    data = requests.post(keys.__get_user_url__, data={'discord_id': discord_id})
    result = data.json()
    if result['code'] == 1:
        mes = result['user'][0][param]
    else:
        mes = 'Ошибка запроса'
    return mes


def get_info(discord_id):
    data = requests.post(keys.__get_user_url__, data={'discord_id': discord_id})
    result = data.json()
    if result['code'] == 1:
        mes = '\n```\n'
        # mes += 'ID: ' + result['user'][0]['u_id'] + '\n'
        mes += 'Выполненно заданий: ' + result['user'][0]['task_count'] + '/' + result['user'][0]['total_count'] + '\n'
        mes += 'Байты: ' + str(round(float(result['user'][0]['points']), 3)) + '\n'
        mes += 'Язык: ' + result['user'][0]['u_class'] + '\n'
        mes += 'Достижений: ' + result['user'][0]['ach_count'] + '\n'
        mes += '```\n'
    else:
        mes = 'Ошибка запроса'
    return mes


def show_help():
    msg = '\n```dsconfig\n'
    msg += '!help - показать помощь\n'
    msg += '!regme <Язык> - зарегистрироваться\n'
    msg += '!change_lang <Язык> - изменить выбранный при регистрации язык\n'
    msg += 'Список доступных языков: '
    for l in Languages:
        msg += l.value + ' '
    msg += '\n'
    msg += '!profile - отобразить ваш профиль\n'
    msg += '!ach - посмотреть список достижений \n'
    # msg += '!inv - просмотреть инвентарь\n'
    msg += '!show_task - получить ссылку на список заданий\n'
    msg += '!show_task <Название> - получить информацию об указанном задании\n'
    msg += '!exec <Название> <Ссылка> - отправить на проверку задачу, указав её название и ссылку на неё. Ссылки ' \
           'принимаются с сайтов https://pastebin.com/ или https://ideone.com/\n'
    msg += 'Сложность задания зависит от цвета. По возростающей от лёгкого до сложного: белый, зелёный, синий, ' \
           'фиолетовый '
    msg += '```\n'
    return msg


def str_to_embed(title, text, points):
    text = parse_task(text).strip()
    embed = discord.Embed(title=title, description=text)
    points = float(points)
    colors = {'common': 0xd5d5d5, 'uncommon': 0x1be700, 'rare': 0x008eff, 'epic': 0xc800e6}
    if 1 <= points < 1.3:
        embed.colour = colors['common']
    elif 1.3 <= points < 1.5:
        embed.colour = colors['uncommon']
    elif 1.5 <= points < 1.7:
        embed.colour = colors['rare']
    elif points >= 1.7:
        embed.colour = colors['epic']

    return embed


def start_scenario_message():
    return ""


def get_phase(pr_ph_id):
    data = requests.post(keys.__get_phase_by_id_url__, data={'pr_ph_id': pr_ph_id})
    js = data.json()
    code = js['code']
    if code == 0:
        return 'Фаза не найдена'
    msg = '```\n'
    msg += js['text']
    msg += '\n```\n'
    return msg


def message_author_is_admin(message):
    return message.author == message.server.owner


def get_item_info(d_id, item_name):
    data = requests.post(keys.__get_item_info_url__, data={'d_id': d_id, 'i_name': item_name})
    print(data.content)
    data = data.json()
    code = data['code']
    msg = ''
    if code == 0:
        msg = 'Предмет не найден'
    elif code == 1:
        msg = '```\n'
        msg += data['i_name']
        if int(data['i_count']) > 1:
            msg += ' (' + data['i_count'] + ') шт.'
        msg += ' - ' + data['i_desc']
        msg += '\n```\n'
    return msg


@client.event
async def on_voice_state_update(before, after):
    data = requests.post(keys.__check_ach_in_voice_url__, data={'d_id': before.id})
    if data.json()['code'] == 1:
        msg = before.mention + ' получил достижение \"' + data.json()['title'] + ' - ' + data.json()['desc'] + '\"'
        channel = before.server.get_channel('519937196891832321')
        await client.send_message(channel, msg)
    elif data.json()['code'] == 0:
        print('Ошибка запроса')
    elif data.json()['code'] == 3:
        print('Пользователь не найден')
    print(data.content)


def add_achievement(user, d_id, a_id):
    data = requests.post(keys.__add_achievement_url__, data={'d_id': d_id, 'a_id': a_id.value})
    print(data.content)
    data = data.json()
    msg = ''
    code = data['code']
    if code == 1:
        msg = user.mention + ' получил достижение \"' + data['title'] + ' - ' + data['desc'] + '\"'
    elif code == 2:
        print('Не возможно найти достижение ' + str(a_id))
    return msg


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    target = message.channel
    msg = ''

    print(message.content)

    if message.content.startswith(BotCommands.HELP.value):
        msg = show_help()

    if message.content.startswith(BotCommands.INV.value):
        msg = get_inv(message.author.id)
        target = message.author

    if message.content.startswith(BotCommands.ACH.value):
        msg = get_achs(message.author.id)
        target = message.author

    if message.content.startswith(BotCommands.GET_ITEM_INFO.value):
        a = message.content.split(' ')
        target = message.author
        if len(a) != 2:
            msg = 'Указаны не все параметры'
        else:
            msg = get_item_info(message.author.id, a[1])

    if message.content.startswith(BotCommands.REMOVE_ITEM.value):
        if message_author_is_admin(message):
            a = message.content.split(' ')
            user_id = re.sub("[<>#@!]", " ", a[1]).strip()
            count = 0
            if len(a) == 3:
                count = 0
            elif len(a) == 4:
                count = a[3]
            msg = remove_item(user_id, a[2], count)
            target = message.server.get_member(user_id)
        else:
            msg = 'У вас не достаточно прав'

    if message.content.startswith(BotCommands.ADD_ITEM.value):
        if message_author_is_admin(message):
            a = message.content.split(' ')
            count = 0
            if len(a) == 3:
                count = 0
            elif len(a) == 4:
                count = a[3]

            user_id = re.sub("[<>#@!]", " ", a[1]).strip()
            msg = add_item(user_id, a[2], count)  # d_id, i_id, count
            target = message.server.get_member(user_id)
        else:
            msg = 'У вас не достаточно прав'

    if message.content.startswith(BotCommands.DISCARD.value):
        if message_author_is_admin(message):
            a = message.content.split(' ')
            if len(a) != 2:
                msg = 'Не верное количество параметров'
            else:
                data = discard(a[1])
                code = data['code']
                if code == 1:
                    msg = 'Задание ' + data['t_name'] + ' отклонено'
                    target = message.server.get_member(data['d_id'])
                elif code == 2:
                    msg = 'Ошибка запроса'
                else:
                    msg = 'Неизвестная ошибка'
        else:
            msg = 'У вас не достаточно прав'

    if message.content.startswith(BotCommands.VALIDATE.value):
        if message_author_is_admin(message):
            a = message.content.split(' ')
            if len(a) != 2:
                msg = 'Не верное количество параметров'
            else:
                data = validate(a[1])
                code = data['code']
                if code == 1:
                    msg = 'Задание ' + data['t_name'] + ' выполнено'
                    user = message.server.get_member(data['d_id'])
                    hello_world_channel = message.server.get_channel('519937196891832321')
                    if data['points'] >= 60:
                        ach_mes = add_achievement(user, data['d_id'], Achievements.GET_2TIER)
                        await client.send_message(hello_world_channel, ach_mes)
                        inc_tier = requests.post(keys.__inc_user_tier_url__, data={'d_id': data['d_id']})
                        data = inc_tier.json()
                    if data['try_c'] == '100':
                        ach_mes = add_achievement(user, data['d_id'], Achievements.TORTURE)
                        await client.send_message(hello_world_channel, ach_mes)
                    target = message.server.get_member(data['d_id'])
                elif code == 2:
                    msg = 'Ошибка запроса'
                else:
                    msg = 'Неизвестная ошибка'
        else:
            msg = 'У вас не достаточно прав'

    if message.content.startswith('!рудз'):
        user = message.server.get_member(message.author.id)
        ach_mes = add_achievement(user, user.id, Achievements.HELP)
        await client.send_message(message.server.get_channel('519937196891832321'), ach_mes)

    if message.content.startswith(BotCommands.EXEC.value):
        a = message.content.split(' ')
        if len(a) != 3:
            msg = 'Не верное количество параметров. Вероятно, вы забыли указать ссылку на решение'
        else:
            msg = push_task(message.author.id, a[1], a[2])
            if msg == 0:
                msg = 'Вы уже выполняли это задание'
            elif msg == 2:
                msg = 'Ошибка запроса'
            elif msg == 3:
                msg = 'Зарегистируйтесь для отправки задачи'
            elif msg == 1:
                msg = 'Ваше задание добавлено в очередь'
            else:
                msg = 'Неизвестная ошибка'

    if message.content.startswith(BotCommands.PROFILE.value):
        msg = get_info(message.author.id)

    if message.content.startswith(BotCommands.START_SCENARIO.value):
        if message_author_is_admin(message):
            msg = start_scenario_message()

    if message.content.startswith(BotCommands.CHANGE_LANG.value):
        a = message.content.split(' ')
        if len(a) != 2:
            msg = 'У этой команды всего 1 параметр - другой язык'
        else:
            if Languages.has_value(a[1]):
                msg = change_lang(a[1], message.author.id)
                if msg == 1:
                    msg = 'Язык изменён на ' + a[1]
                else:
                    msg = 'Ошибка запроса'
            else:
                msg = 'Не верный язык'

    if message.content.startswith(BotCommands.START_PHASE.value):
        if message_author_is_admin(message):
            a = message.content.split(' ')
            if len(a) != 2:
                msg = 'Не указан id фазы'
            else:
                msg = '@everyone\n'
                msg += get_phase(a[1])
                channel = message.server.get_channel('519937196891832321')
                target = channel
                await client.send_message(target, msg)
                return

    if message.content.startswith(BotCommands.GET_MAX_POINTS.value):
        msg = str(round(float(get_max_points()), 3))

    if message.content.startswith(BotCommands.REGME.value):
        a = message.content.split(' ')
        if len(a) != 2:
            msg = 'Вы не указали все необходимые параметры для регистрации'
        else:
            msg = reg(message.author.id, a[1])
            if msg == 1:
                msg = 'Вы успешно зарегистировались\n'
                msg += add_item(message.author.id, 1, 1)
                target = message.server.get_member(message.author.id)
            elif msg == 2:
                msg = 'Вы уже зарегистрированы'
            elif msg == 3:
                msg = 'Нельзя выбрать этот язык. Используйте !help чтобы узнать подробности'
            else:
                msg = 'Ошибка запроса'

    if message.content.startswith(BotCommands.SHOW_TASK.value):
        target = message.author
        a = message.content.split(' ')
        try:
            if len(a) == 2:
                res = get_task_by_name(a[1])
                embed = str_to_embed(task_format(res)['Name'], task_format(res)['Text'], task_format(res)['Points'])
                await client.send_message(target, embed=embed)
                return
            elif len(a) == 1:
                u_id = get_user_info(message.author.id, 'u_id')
                msg = keys.__get_tasklist_url__ + '?u_id=' + u_id
            else:
                raise KeyError
        except KeyError:
            msg = 'Задание с таким названием не найдено'

    if msg:
        await client.send_message(target, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('---')
    game = discord.Game(name='Life simulator')
    await client.change_presence(game=game)


client.run(keys.__TOKEN__)
# client.run(keys.__TOKEN_BAKA__)
