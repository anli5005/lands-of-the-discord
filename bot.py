import asyncio
import discord
from discord.ext import commands
import json
from pymongo import MongoClient

from xp import XPManager
from resource import ResourcesManager
from mining import MineManager

mongoURL = "mongodb://localhost:27017"
token = "SEE-CONFIG-JSON"
roles = {"viewInventories": "", "resetCooldowns": ""}
with open("config.json") as f:
    config = json.loads(f.read())
    mongoURL = config["mongo"]
    token = config["token"]
    roles = config["roles"]
client = MongoClient(mongoURL)
db = client.lotd

res = []
with open("resources.json") as f:
    res = json.loads(f.read())

mines = {}
with open("mines.json") as f:
    mines = json.loads(f.read())

bot = commands.Bot(command_prefix = "!")
xpm = XPManager(db)
resources = ResourcesManager(db, res)
mining = MineManager(db, mines, resources, xpm)

def has_permission(member, permission):
    for role in member.roles:
        if role.id == roles[permission]:
            return True
    return False

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

@bot.command()
async def ping():
    await bot.say("Pong!")

@bot.command(pass_context = True)
async def xp(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    await bot.say("<@!{}> has {} XP".format(member.id, xpm.getXP(member.id)))

@bot.command(pass_context = True)
async def mine(ctx):
    text = mining.mineChannel(ctx.message.author.id, ctx.message.channel.id)
    if text:
        await bot.say(text)

@bot.command(pass_context = True)
async def inventory(ctx, member: discord.Member = None):
    if (not has_permission(ctx.message.author, "viewInventories")) or member is None:
        member = ctx.message.author
    inventory = resources.getInventory(member.id)
    embed = discord.Embed(title = member.name, description = "Inventory")
    embed.add_field(name = "🌠 XP", value = xpm.getXP(member.id), inline = False)
    embeds = [embed]
    for item in inventory:
        resource = resources.resourceDict[item["resource"]]
        embed.add_field(name = "{} {}".format(resource["emoji"], resource["plural"]), value = item["count"])
        if len(embed.fields) >= 25:
            embed = discord.Embed(title = member.name, description = "Inventory (continued)")
            embeds.append(embed)
    await bot.say("Here's <@!{}>'s inventory:".format(member.id))
    for e in embeds:
        await bot.send_message(ctx.message.channel, embed = e)

bot.run(token)
