import discord
import asyncio
import random
import os
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

Discord = {
    'token': config['bot']['token'],
    'channel_id': config['bot']['channel_id'],
    'channel': config['bot']['channel']
}

bot = discord.Client()


@bot.event
@asyncio.coroutine
def on_message(message):
    # print(message.author)
    print(message.content)

    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if message.content.startswith('/hello'):
        msg = 'Hello {0.author.mention}. Have a :pancakes:'.format(message)
        yield from bot.send_message(message.channel, msg)
    elif message.content.startswith('/sticker'):
        tok = message.content.split(' ')
        if len(tok) < 2:
            msg = "Specify sticker name"
            yield from bot.send_message(message.channel, msg)
        else:
            sticker_name = tok[1]
            file_name = "stickers/{}.png".format(sticker_name)
            if os.path.exists(file_name):
                yield from bot.send_file(message.channel, file_name)
            else:
                msg = "No sticker found :gaze:"
                yield from bot.send_message(message.channel, msg)
    elif message.content.startswith('/dice'):
        tok = message.content.split(' ')
        if len(tok) < 2:
            msg = "Specify nuber of sides"
        else:
            sides = int(tok[1])
            if sides > 3:
                random.seed()
                number = random.randrange(1, sides, 1)
                msg = "A dice rolled {}".format(number)
            else:
                msg = "What a dice is that??"
        yield from bot.send_message(message.channel, msg)


@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    channel = discord.Object(id='277941647139012609')
    yield from bot.send_message(channel, "Heya")


bot.run(Discord['token'])
