import asyncio
import discord
from discord.ext import commands
import json
import math
from pymongo import MongoClient

from auditing import AuditingManager
from xp import XPManager
from resource import ResourcesManager
from mining import MineManager

mongoURL = "mongodb://localhost:27017"
token = "SEE-CONFIG-JSON"
roles = {"viewInventories": "", "resetCooldowns": "", "editInventories": ""}
exponent = 1.5
quitcommand = False
prefix = "!"
levelupchannel = ""
with open("config.json", encoding = "utf-8") as f:
    config = json.loads(f.read())
    mongoURL = config["mongo"]
    token = config["token"]
    roles = config["roles"]
    exponent = config["levelUpExponent"]
    quitcommand = config["quitCommand"]
    levelupchannel = config["levelUpChannel"]
    prefix = config["prefix"]
client = MongoClient(mongoURL)
db = client.lotd

res = []
with open("resources.json", encoding = "utf-8") as f:
    res = json.loads(f.read())

mines = {}
with open("mines.json", encoding = "utf-8") as f:
    mines = json.loads(f.read())

bot = commands.Bot(command_prefix = prefix)
xpm = XPManager(db, exponent)
resources = ResourcesManager(db, res)
mining = MineManager(db, mines, resources, xpm)
audit = AuditingManager(db)

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
    text = await mining.mineChannel(ctx.message.author.id, ctx.message.channel.id)
    if text:
        await bot.say(text)

@bot.command(pass_context = True)
async def inventory(ctx, member: discord.Member = None):
    if (not has_permission(ctx.message.author, "viewInventories")) or member is None:
        member = ctx.message.author
    inventory = resources.getInventory(member.id)
    embed = discord.Embed(title = member.name, description = "Inventory")
    xp = xpm.getXP(member.id)
    embed.add_field(name = "🌠 XP", value = "{} (Lvl {})".format(xp, math.floor(xpm.getLevelFromXP(xp))), inline = False)
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

@bot.command(pass_context = True)
async def give(ctx, member: discord.Member, count: int, * res: str):
    resource = resources.resolveResource(" ".join(res))
    if resource:
        if count > 0:
            if resources.getResource(ctx.message.author.id, resource) >= count:
                resources.updateResource(ctx.message.author.id, resource, -1 * count)
                resources.updateResource(member.id, resource, count)
                await bot.say("Gave {} {} to <@!{}>".format(count, resources.resourceDict[resource]["singular" if count == 1 else "plural"], member.id))
            else:
                await bot.say("You don't have enough {}.".format(resources.resourceDict[resource]["plural"]))
        elif count == 0:
            await bot.say("Please supply a positive number.")
        else:
            await bot.say("Woah woah woah! What are you trying to pull?!")
    else:
        await bot.say("That resource doesn't exist.")

@bot.command(pass_context = True)
async def forcegive(ctx, member: discord.Member, count: int, * res: str):
    if has_permission(ctx.message.author, "editInventories"):
        resource = resources.resolveResource(" ".join(res))
        if resource:
            audit.log("force_give", ctx.message.author, {"target": member.id, "resource": resource, "count": count})
            resources.updateResource(member.id, resource, count)
            await bot.say("Gave {} {} to <@!{}> out of thin air".format(count, resources.resourceDict[resource]["singular" if count == 1 else "plural"], member.id))
            await bot.say("*Added an entry to the audit log*")
        else:
            await bot.say("That resource doesn't exist.")
    else:
        await bot.say("You don't have permission to use this command.")

@bot.command(pass_context = True)
async def forcexp(ctx, action: str, member: discord.Member, count: int):
    if has_permission(ctx.message.author, "editInventories"):
        if action == "add":
            await xpm.awardXP(member.id, count)
            await bot.say("Forcibly gave {} XP to <@!{}>".format(count, member.id))
        elif action == "set":
            xpm.setXP(member.id, count)
            await bot.say("Forcibly set <@!{}>'s XP to {}".format(member.id, count))
        else:
            await bot.say("Usage: `!forcexp (add|set) <member> <xp>`")
            return
        audit.log("force_xp", ctx.message.author, {"target": member.id, "action": action, "count": count})
        await bot.say("*Added an entry to the audit log*")
    else:
        await bot.say("You don't have permission to use this command.")

@bot.command(pass_context = True)
async def resetcooldowns(ctx, member: discord.Member):
    if has_permission(ctx.message.author, "editInventories"):
        audit.log("reset_cooldowns", ctx.message.author, {"target": member.id})
        db.mining.delete_many({"discordID": member.id})
        await bot.say("Reset mining cooldowns for {}".format(member.name))
        await bot.say("*Added an entry to the audit log*")
    else:
        await bot.say("You don't have permission to use this command.")

if quitcommand:
    @bot.command(pass_context = True)
    async def quit(ctx):
        audit.log("quit", ctx.message.author, {})
        await bot.say("Quitting...")
        exit()

@xpm.onLevelUp
async def levelUp(user, level):
    if levelupchannel != "":
        await bot.send_message(discord.Object(id = levelupchannel), "<@!{}> has reached level {}!".format(user, level))

bot.run(token)
