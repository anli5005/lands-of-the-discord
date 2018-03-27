from manager import Manager

class XPManager(Manager):
    def getXP(self, user):
        xp = self.db.xp.find_one({"discordID": user})
        if xp:
            return xp["xp"]
        else:
            return 0

    def awardXP(self, user, xp):
        self.db.xp.update_one({"discordID": user}, {"$inc": {"xp": xp}}, upsert = True)

    def setXP(self, user, xp):
        self.db.xp.update_one({"discordID": user}, {"$set": {"xp": xp}}, upsert = True)
