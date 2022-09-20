import aiohttp
import json
import copy
from typing import Dict, Union
from fastapi import Response

from app.models.DataStorage import PrsDataStorageEntry
from app.models.Tag import PrsTagEntry
from app.svc.Services import Services as svc

class PrsVictoriametricsEntry(PrsDataStorageEntry):

    def __init__(self, **kwargs):
        super(PrsVictoriametricsEntry, self).__init__(**kwargs)

        self.tag_cache = {}
        if isinstance(self.data.attributes.prsJsonConfigString, dict):
            js_config = self.data.attributes.prsJsonConfigString
        else:
            js_config = json.loads(self.data.attributes.prsJsonConfigString)
        self.put_url = js_config['putUrl']
        self.get_url = js_config['getUrl']

        #self.session = None
        self.session = aiohttp.ClientSession()

    def _format_data_store(self, tag: PrsTagEntry) -> Union[None, Dict]:
        if tag.data.attributes.prsStore:
            data_store = json.loads(tag.data.attributes.prsStore)
        else:
            data_store = {}
        if data_store.get('metric') is None:
            data_store['metric'] = (tag.data.attributes.cn, tag.data.attributes.cn[0])[isinstance(tag.data.attributes.cn, list)] # cn is array of str!

            # имя метрики не может начинаться с цифр и не может содержать дефисов
            if tag.id == data_store['metric']:
                data_store['metric'] = "t_{}".format(data_store['metric'].replace('-', '_'))

        return data_store

    async def connect(self) -> int:
        #if self.session is None:
        #    self.session = aiohttp.ClientSession()
        async with self.session.get("{}{}".format(self.get_url, "?match[]=vm_free_disk_space_bytes")) as response:
            return response.status

    async def set_data(self, data):
        # data:
        # {
        #        "<tag_id>": [(x, y, q)]
        # }
        #
        # method forms archive:
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
            # формат prsStore у тэга:
            #
            #   {
            #        "metric": "metric_name",
            #        "tags": {
            #            "t1": "v1",
            #            "t2": "v2"
            #        }
            #    }
            tag_metric = svc.get_tag_cache(key, "data_storage")
            for data_item in item:
                x, y, _ = data_item
                tag_metric['value'] = y
                tag_metric['timestamp'] = round(x / 1000)
                formatted_data.append(copy.deepcopy(tag_metric))

        resp = await self.session.post(self.put_url, json=formatted_data)

        svc.logger.debug(f"Set data status: {resp.status}")

        return Response(status_code=resp.status)
