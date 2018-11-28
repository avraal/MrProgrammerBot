import discord
import requests
import sys
sys.path.append('../')
from src import keys
from src.botcommands import BotCommands

client = discord.Client()


def get_task_by_name(name):
    data = requests.post(keys.__get_all_tasks_url__, data={'pr_t_name': name})
    return data.json()['task'][0]


def task_format(json):
    task = {'Name': json['pr_t_name'], 'Text': json['pr_t_text'], 'Points': json['pr_t_points']}
    return task


def reg(author_id):
    data = requests.post(keys.__reg_url__, data={'user_id': author_id})
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
        mes += 'Очки: ' + result['user'][0]['points'] + '\n'
        mes += '```\n'
    else:
        mes = 'Ошибка запроса'
    return mes


def show_help():
    msg = '\n```dsconfig\n'
    msg += '!help - показать помощь\n'
    msg += '!regme - зарегистрироваться\n'
    msg += '!profile - отобразить ваш профиль\n'
    msg += '!show_task - получить ссылку на список заданий\n'
    msg += '!exec <Название> <Ссылка> - отправить на проверку задачу, указав её название и ссылку на неё. Ссылки ' \
           'принимаются с сайтов https://pastebin.com/ или https://ideone.com/'
    msg += '```\n'
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

    if message.content.startswith(BotCommands.REGME.value):
        msg = reg(message.author.id)
        if msg == 1:
            msg = 'Вы успешно зарегистировались'
        elif msg == 2:
            msg = 'Вы уже зарегистрированы'
        else:
            msg = 'Ошибка запроса'

    if message.content.startswith(BotCommands.SHOW_TASK.value):
        target = message.author
        a = message.content.split(' ')
        try:
            if len(a) != 2:
                raise KeyError
            res = get_task_by_name(a[1])
            msg = '```\n' + task_format(res)['Name'] + '\n'
            msg += task_format(res)['Text'] + '\n'
            # msg += 'Points: '
            msg += '\n```\n'
            # msg += str(task_format(res)['Points']) + '\n```\n'
        except KeyError:
            msg = 'Задание с таким названием не найдено'

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
