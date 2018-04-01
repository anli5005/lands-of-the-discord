import time
from manager import Manager

class AuditingManager(Manager):
    def log(self, action, member, meta):
        audit = {"time": time.time(), "action": action, "meta": meta}
        if member:
            audit["discordID"] = member.id
        self.db.audit.insert_one(audit)
