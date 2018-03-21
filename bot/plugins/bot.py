import json
from pymongo import MongoClient
from disco.bot import Plugin, Config

class LOTDBotPlugin(Plugin):
    mongoURL = "mongodb://localhost:27017"

    def load(self, ctx):
        super(LOTDBotPlugin, self).load(ctx)
        with open("config.json") as f:
            config = json.loads(f.read())
            self.mongoURL = config["mongo"]
        self.client = MongoClient(self.mongoURL)
        self.db = self.client.lotd

    @Plugin.command("ping")
    def command_ping(self, event):
        event.msg.reply("Pong!")
