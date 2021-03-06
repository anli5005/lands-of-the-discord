from manager import Manager

class ResourcesManager(Manager):
    def __init__(self, db, resources):
        super().__init__(db)
        self.resources = resources
        self.resourceDict = {}
        for resource in self.resources:
            self.resourceDict[resource["id"]] = resource

    def getResource(self, user, resource):
        resources = self.db.resources.find_one({"discordID": user})
        if resources and resources[resource]:
            return resources[resource]
        else:
            return 0

    def updateResource(self, user, resource, amount):
        if self.resourceDict[resource]:
            self.db.resources.update_one({"discordID": user}, {"$inc": {resource: amount}}, upsert = True)

    def getInventory(self, user):
        inventory = []
        resources = self.db.resources.find_one({"discordID": user})
        if resources:
            for resource in self.resources:
                if resource["id"] in resources and resources[resource["id"]] != 0:
                    inventory.append({"resource": resource["id"], "count": resources[resource["id"]]})
                elif "alwaysInInventory" in resource and resource["alwaysInInventory"]:
                    inventory.append({"resource": resource["id"], "count": 0})
        return inventory

    def resolveResource(self, message):
        text = message.lower()
        for resource in self.resources:
            if resource["id"].lower() == text or resource["singular"].lower() == text or resource["plural"].lower() == text or resource["emoji"] == message:
                return resource["id"]
        return None
