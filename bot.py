from imports import *

async def run():
    bot = Bot()
    await bot.start(config.bot_token)

class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self._get_prefix)
        self.things = {}
        self.loop.create_task(self.load_modules())

    async def _get_prefix(self, bot, message):
        prefix = returnPrefix(message)
        return commands.when_mentioned_or(prefix)(bot, message)

    async def load_modules(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)
        modules = [x.stem for x in Path('modules').glob('*.py')]
        for module in modules:
            try:
                self.load_extension(f'modules.{module}')
                print(f'Successfully loaded {module}')
            except Exception as e:
                print(f'Failed to load {module} : {e}')

    async def on_ready(self):
        self.loop.create_task(self.reload_module())

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == 516976377979994113 or message.channel.id == 516254244022648837 or message.channel == message.author.dm_channel:
            await self.process_commands(message)

    async def reload_module(self):
        while True:
            modules = [x.stem for x in Path('modules').glob('*.py')]
            files = []
            channel = self.get_channel(514057242396327964)
            for module in modules:
                files.append(f'modules/{module}.py')

            for file in files:
                f = open(file, 'r')
                try:
                    if self.things[file] == f.read():
                        pass
                    else:
                        x = open(file, 'r')
                        self.things[file] = x.read()
                        try:
                            self.unload_extension(f'modules.{file[8:-3]}')
                            self.load_extension(f'modules.{file[8:-3]}')
                            await channel.send(f"Successfully reloaded {file}")
                        except Exception as e:
                            await channel.send(f"Failed to reload {file}\nError : {e}")
                except:
                    self.things[file] = f.read()

            await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
