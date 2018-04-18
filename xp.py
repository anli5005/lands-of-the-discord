import math
from manager import Manager

class XPManager(Manager):
    def __init__(self, db, exponent):
        super().__init__(db)
        self.exponent = exponent

    def getXP(self, user):
        xp = self.db.xp.find_one({"discordID": user})
        if xp:
            return xp["xp"]
        else:
            return 0

    def getLevelFromXP(self, xp):
        return xp ** (1 / self.exponent)

    def getXPForLevel(self, level):
        return math.floor(level ** self.exponent) + 1

    async def awardXP(self, user, xp):
        oldlevel = math.floor(self.getLevelFromXP(self.getXP(user)))
        self.db.xp.update_one({"discordID": user}, {"$inc": {"xp": xp}}, upsert = True)
        newlevel = math.floor(self.getLevelFromXP(self.getXP(user)))
        for level in range(oldlevel + 1, newlevel + 1):
            await self.handleLevelUp(user, level)

    def setXP(self, user, xp):
        self.db.xp.update_one({"discordID": user}, {"$set": {"xp": xp}}, upsert = True)

    async def handleLevelUp(self, user, level):
        if self.levelUpHandler:
            await self.levelUpHandler(user, level)

    def onLevelUp(self, function):
        self.levelUpHandler = function
        return function
