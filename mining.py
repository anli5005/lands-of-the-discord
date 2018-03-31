import time
from datetime import datetime
from manager import Manager

class MineManager(Manager):
    def __init__(self, db, mines, resources, xp):
        super().__init__(db)
        self.mines = mines
        self.resources = resources
        self.xp = xp

    def mine(self, user, mine):
        mineCooldown = self.db.mining.find_one({"discordID": user, "mineID": mine["id"]})
        currentTime = time.time()
        if mineCooldown and mineCooldown["time"] + mine["cooldown"] > currentTime:
            return "Please wait {} before mining in this channel again.".format(str(datetime.fromtimestamp(round(mine["cooldown"] + mineCooldown["time"])) - datetime.fromtimestamp(round(currentTime))))
        else:
            if mine["xp"]:
                self.xp.awardXP(user, mine["xp"])
            self.resources.updateResource(user, mine["resource"], mine["quantity"])
            message = mine["message"].replace("{quantity}", str(mine["quantity"])).replace("{xp}", str(mine["xp"]))
            self.db.mining.update_one({"discordID": user, "mineID": mine["id"]}, {"$set": {"time": currentTime}}, upsert = True)
            if mine["quantity"] == 1:
                return message.replace("{resource}", self.resources.resourceDict[mine["resource"]]["singular"])
            else:
                return message.replace("{resource}", self.resources.resourceDict[mine["resource"]]["plural"])

    def mineChannel(self, user, channel):
        if channel in self.mines:
            return self.mine(user, self.mines[channel])
        else:
            return "You can't mine in this channel."
