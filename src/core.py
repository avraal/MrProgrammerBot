import discord
import requests
import sys

sys.path.append('../')
from src import keys
from src.botcommands import BotCommands
from enum import Enum, unique


@unique
class Languages(Enum):
    CPP = 'C++'
    CS = 'C#'
    WEB = 'Web'


client = discord.Client()


def get_task_by_name(name):
    data = requests.post(keys.__get_all_tasks_url__, data={'pr_t_name': name})
    return data.json()['task'][0]


def parse_task(task):
    task = task.replace('<br>', '')
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


def validate(id_in_stack):
    data = requests.post(keys.__validate_url__, data={'id_in_stack': id_in_stack})
    print(data.content)
    return data.json()['code']


def get_info(discord_id):
    data = requests.post(keys.__get_user_url__, data={'discord_id': discord_id})
    result = data.json()
    print(result['user'][0])
    if result['code'] == 1:
        mes = '\n```\n'
        mes += 'Выполненно заданий: ' + result['user'][0]['task_count'] + '\n'
        mes += 'Байты: ' + result['user'][0]['points'] + '\n'
        mes += 'Язык: ' + result['user'][0]['u_class'] + '\n'
        mes += '```\n'
    else:
        mes = 'Ошибка запроса'
    return mes


def show_help():
    msg = '\n```dsconfig\n'
    msg += '!help - показать помощь\n'
    msg += '!regme <Язык> - зарегистрироваться\n'
    msg += 'Список доступных языков: '
    for l in Languages:
        msg += l.value + ' '
    msg += '\n'
    msg += '!profile - отобразить ваш профиль\n'
    msg += '!show_task - получить ссылку на список заданий\n'
    msg += '!show_task <Название> - получить информацию об указанном задании\n'
    msg += '!exec <Название> <Ссылка> - отправить на проверку задачу, указав её название и ссылку на неё. Ссылки ' \
           'принимаются с сайтов https://pastebin.com/ или https://ideone.com/\n'
    msg += 'Сложность задания зависит от цвета. По возростающей от лёгкого до сложного: белый, зелёный, синий, ' \
           'фиолетовый '
    msg += '```\n'
    return msg


def str_to_embed(title, text, points):
    text = parse_task(text)
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


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    target = message.channel
    msg = ''

    print(message.content)

    if message.content.startswith(BotCommands.HELP.value):
        msg = show_help()

    if message.content.startswith(BotCommands.VALIDATE.value):
        if message.author == message.server.owner:
            a = message.content.split(' ')
            if len(a) != 2:
                msg = 'Не верное количество параметров'
            else:
                msg = validate(a[1])
                if msg == 1:
                    msg = 'Задание выполнено'
                elif msg == 2:
                    msg = 'Ошибка запроса'
                else:
                    msg = 'Неизвестная ошибка'
        else:
            msg = 'У вас не достаточно прав'

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
        if message.author == message.server.owner:
            msg = start_scenario_message()

    if message.content.startswith(BotCommands.START_PHASE.value):
        if message.author == message.server.owner:
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

    if message.content.startswith(BotCommands.REGME.value):
        a = message.content.split(' ')
        if len(a) != 2:
            msg = 'Вы не указали все необходимые параметры для регистрации'
        else:
            msg = reg(message.author.id, a[1])
            if msg == 1:
                msg = 'Вы успешно зарегистировались'
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
                msg = keys.__get_tasklist_url__
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
