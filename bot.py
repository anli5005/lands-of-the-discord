import asyncio
import discord
import json
from pymongo import MongoClient

from xp import XPManager

mongoURL = "mongodb://localhost:27017"
token = "SEE-CONFIG-JSON"
with open("config.json") as f:
    config = json.loads(f.read())
    mongoURL = config["mongo"]
    token = config["token"]
client = MongoClient(mongoURL)
db = client.lotd

bot = discord.Client()
xp = XPManager(db)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

@bot.event
async def on_message(message):
    if message.content == "!ping":
        await bot.send_message(message.channel, "Pong!")
    elif message.content == "!instantxp":
        await bot.send_message(message.channel, "Gave you 100 XP instantly")
        xp.awardXP(message.author.id, 100)
    elif message.content == "!xp":
        await bot.send_message(message.channel, "You have {} XP.".format(xp.getXP(message.author.id)))

bot.run(token)
