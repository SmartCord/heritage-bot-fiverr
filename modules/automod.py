from imports import *

class AutoMod:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == 516944445091086336:
            messag = f"{message.author} : ```{message.content}```"
            wowcoolchannellollmaokysbyeugay = self.bot.get_channel(516946274302558209)
            await wowcoolchannellollmaokysbyeugay.send(messag)
            await message.delete()

def setup(bot):
    bot.add_cog(AutoMod(bot))
