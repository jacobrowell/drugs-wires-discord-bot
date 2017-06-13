import traceback
import discord
import configparser
import inspect
import random
import os


class Response:
    def __init__(self, content, reply=False, delete_after=0):
        self.content = content
        self.reply = reply
        self.delete_after = delete_after


class DNWBot(discord.Client):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.auth = (self.config['credentials']['token'],)
        self.command_prefix = '/'
        super().__init__()

    async def cmd_hello(self, author):
        msg = 'Hello {}. Have a :pancakes:'.format(author.mention)
        return Response(msg)

    async def cmd_sticker(self, channel, sticker_name=None):
        if sticker_name:
            file_name = "stickers/{}.png".format(sticker_name)
            if os.path.exists(file_name):
                await self.send_file(channel, file_name)
                msg = False
            else:
                msg = "No sticker found :eyes:"
        else:
            msg = "Specify sticker name"

        if msg:
            return Response(msg)
        else:
            return False

    async def cmd_stickers(self):
        files = os.listdir('stickers')
        names = sorted(map(lambda name: name.replace('.png', ''), files))
        msg = ', '.join(names)
        msg = 'Here are all the available stickers:\n' + msg

        return Response(msg)

    async def cmd_dice(self, sides=6):
        sides = int(sides)
        if sides > 1:
            random.seed()
            number = random.randrange(1, sides, 1)
            msg = "A dice rolled {}".format(number)
        elif sides == 0:
            msg = "Answer is 1, what did you expect?"
        else:
            msg = "What a dice is that??"

        return Response(msg)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        await self.wait_until_ready()

        message_content = message.content.strip()
        if not message_content.startswith(self.command_prefix):
            return

        if message.author == self.user:
            print("Ignoring command from myself (%s)" % message.content)
            return

        command, *args = message_content.split()
        command = command[len(self.command_prefix):].lower().strip()

        handler = getattr(self, 'cmd_%s' % command, None)
        if not handler:
            return

        # if message.channel.is_private:
        #     if not (message.author.id == self.config.owner_id and command == 'joinserver'):
        #         await self.send_message(message.channel, 'You cannot use this bot in private messages.')
        #         return

        else:
            print("[Command] {0.id}/{0.name} ({1})".format(message.author, message_content))

        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()

        # noinspection PyBroadException
        try:
            handler_kwargs = {}
            if params.pop('message', None):
                handler_kwargs['message'] = message

            if params.pop('channel', None):
                handler_kwargs['channel'] = message.channel

            if params.pop('author', None):
                handler_kwargs['author'] = message.author

            if params.pop('server', None):
                handler_kwargs['server'] = message.server

            if params.pop('leftover_args', None):
                handler_kwargs['leftover_args'] = args

            args_expected = []
            for key, param in list(params.items()):
                doc_key = '[%s=%s]' % (key, param.default) if param.default is not inspect.Parameter.empty else key
                args_expected.append(doc_key)

                if not args and param.default is not inspect.Parameter.empty:
                    params.pop(key)
                    continue

                if args:
                    arg_value = args.pop(0)
                    handler_kwargs[key] = arg_value
                    params.pop(key)

            if params:
                docs = getattr(handler, '__doc__', None)
                if not docs:
                    docs = 'Usage: {}{} {}'.format(
                        self.command_prefix,
                        command,
                        ' '.join(args_expected)
                    )

                docs = '\n'.join(l.strip() for l in docs.split('\n'))
                await self.send_message(
                    message.channel,
                    '```\n%s\n```' % docs.format(command_prefix=self.command_prefix)
                )
                return

            response = await handler(**handler_kwargs)
            if response and isinstance(response, Response):
                content = response.content
                if response.reply:
                    content = '%s, %s' % (message.author.mention, content)

                sentmsg = await self.send_message(message.channel, content)

        except Exception:
            traceback.print_exc()

    def run(self):
        try:
            self.loop.run_until_complete(self.start(*self.auth))

        except discord.errors.LoginFailure:
            # Add if token, else
            print("""
                Bot cannot login, bad credentials.
                Fix your Email or Password or Token in the options file.
                "Remember that each field should be on their own line.")
                """)
