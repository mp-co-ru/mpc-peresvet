import json
from random import randrange, uniform

from locust import HttpUser, task, between

class DataSetUser(HttpUser):
    #wait_time = between(0.5, 1)

    @task
    def set_data(self):
        i = randrange(len(self._ids["ids"]))
        data_item = {}
        if self._ids["ids"][i]["type"] == 1:
            data_item["y"] = uniform (-100, 100)
        else:
            data_item["y"] = randrange (-100, 100)

        data = {
            "data": [
                {
                    "tagId": self._ids["ids"][i]["id"],
                    "data": [
                        data_item
                    ]
                }
            ]
        }

        #data = {"data": [{"tagId": "635ecc7c-af4f-103c-9bc4-f315a0a65dfc", "data": [{"y": 29.998314224725192}]}]}
        self.client.post("/data", json=data)

    '''
    @task(3)
    def view_items(self):
        for item_id in range(10):
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)
    '''

    def on_start(self):
        with open("/mnt/locust/ids.json", "r") as f:
            self._ids = json.load(f)
        #self.client.post("/login", json={"username":"foo", "password":"bar"})
