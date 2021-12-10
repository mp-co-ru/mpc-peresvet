import aiohttp
import json
from app.models.DataStorage import PrsDataStorageEntry
import app.main as main

class PrsVictoriametricsEntry(PrsDataStorageEntry):

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)

        self.tag_cache = {}
        js_config = json.loads(self.data.attributes.prsJsonConfigString)
        self.put_url = js_config['putUrl']
        self.get_url = js_config['getUrl']

        self.session = aiohttp.ClientSession()

    async def connect(self) -> int:
        async with self.session.get("{}{}".format(self.get_url, "?match[]=vm_free_disk_space_bytes")) as response:
            return response.status
            