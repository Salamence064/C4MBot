from dotenv import dotenv_values
import discord


# import token from .env file
env = dotenv_values(".env") # will give us a dictionary with all values from .env


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if (self.user.id == env["BOT_ID"]): return
        if (message.content == "hello"): await message.channel.send("Hello World")


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(env["TOKEN"])
