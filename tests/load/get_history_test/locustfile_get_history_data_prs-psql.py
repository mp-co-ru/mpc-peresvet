import json
import random
import string
from datetime import datetime, timedelta

from locust import HttpUser, TaskSet, task, between, events

from websocket import create_connection
import time

import times

class DataGetHistoryUser(HttpUser):

    def on_start(self):
        with open("/mnt/locust/tags_in_postgres.json", "r") as f:
            js = json.load(f)
            self.ids = js["0"]
            '''
            self.ids += js["1"]
            self.ids += js["2"]
            self.ids += js["4"]
            '''

        self.pack_size = self.environment.parsed_options.tags_in_pack
        self.start_date = self.environment.parsed_options.start
        self.payload = {
            "tagId": []
        }
        if self.start_date:
            self.payload["start"] = times.ts(self.start_date)
        self.end_date = self.environment.parsed_options.finish
        if self.end_date:
            self.payload["finish"] = times.ts(self.end_date)


    @task
    def get_data(self):
        self.payload["tagId"] = random.sample(self.ids, self.pack_size)

        self.client.get("", json=self.payload)
