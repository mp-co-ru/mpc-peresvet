import aiohttp
import json
import copy
from typing import Dict, Union
from app.models.DataStorage import PrsDataStorageEntry
from app.svc.Services import Services as svc

class PrsVictoriametricsEntry(PrsDataStorageEntry):

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)

        self.tag_cache = {}
        js_config = json.loads(self.data.attributes.prsJsonConfigString)
        self.put_url = js_config['putUrl']
        self.get_url = js_config['getUrl']

        self.session = aiohttp.ClientSession()

    def _format_data_store(self, attrs: Dict) -> Union[None, Dict]:
        data_store = json.loads(attrs['prsDataStore'])
        if data_store['metric'] is None:
            data_store['metric'] = attrs.cn
        return data_store

    async def connect(self) -> int:
        async with self.session.get("{}{}".format(self.get_url, "?match[]=vm_free_disk_space_bytes")) as response:
            return response.status
            
    async def set_data(self, data):
        #{
        #        "<tag_id>": [(x, y, q)]
        #}  
        # 
        # [
        #     {
        #         "metric": "sys.cpu.nice",
        #         "timestamp": 1346846400,
        #         "value": 18,
        #         "tags": {
        #            "host": "web01",
        #            "dc": "lga"
        #         }
        #     },
        #     {
        #         "metric": "sys.cpu.nice",
        #         "timestamp": 1346846400,
        #         "value": 9,
        #         "tags": {
        #            "host": "web02",
        #            "dc": "lga"
        #         }
        #     }
        # ] 
        
        formatted_data = []
        for key, item in data.items():
            # формат prsDataStore у тэга:
            # 
            #   {
            #        "metric": "metric_name",
            #        "tags": {
            #            "t1": "v1",
            #            "t2": "v2"
            #        }
            #    }
            metric_tag = self.tags_cache[key]
            for data_item in item:
                x, y, q = data_item
                metric_tag['value'] = y
                metric_tag['timestamp'] = x / 1000
                formatted_data.append(copy.deepcopy(metric_tag))

        async with aiohttp.ClientSession() as session:
            resp = await session.post(self.put_url, data=formatted_data)
            svc.logger.debug("Set data status: {}".format(resp.status))