import json
from app.models.DataStorage import PrsDataStorageEntry
import app.main as main

class PrsVictoriametrics(PrsDataStorageEntry):

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)

        self.tag_cache = {}
        js_config = json.loads(self.data.attributes.prsJsonConfigString)
        self.putUrl = js_config['putUrl']
        self.getUrl = js_config['getUrl']

    def connect(self):
        pass