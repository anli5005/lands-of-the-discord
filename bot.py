import asyncio
import discord
import json
from pymongo import MongoClient

from xp import XPManager
from resource import ResourcesManager

mongoURL = "mongodb://localhost:27017"
token = "SEE-CONFIG-JSON"
with open("config.json") as f:
    config = json.loads(f.read())
    mongoURL = config["mongo"]
    token = config["token"]
client = MongoClient(mongoURL)
db = client.lotd

resources = []
with open("resources.json") as f:
    resources = json.loads(f.read())

bot = discord.Client()
xp = XPManager(db)
resources = ResourcesManager(db, resources)

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
    elif message.content == "!instantlava":
        resources.updateResource(message.author.id, "lavastone", 1)
    elif message.content == "!inventory":
        inventory = resources.getInventory(message.author.id)
        embed = discord.Embed(title = message.author.name, description = "Inventory")
        for item in inventory:
            resource = resources.resourceDict[item["resource"]]
            embed.add_field(name = "{} {}".format(resource["emoji"], resource["plural"]), value = item["count"])
        await bot.send_message(message.channel, "{}, here's your inventory:".format(message.author.name), embed = embed)
bot.run(token)
