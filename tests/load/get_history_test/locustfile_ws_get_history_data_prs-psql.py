
import json
import random
import string
import websocket
import gevent
from datetime import datetime, timedelta

from locust import User, task, events

from websocket import create_connection
import time
import times

from uuid import uuid4

#from locust_plugins.users import SocketIOUser

class WSDataGetHistoryUser(User):

    def on_start(self):
        """
        with open("/mnt/locust/tags_in_postgres.json", "r") as f:
            js = json.load(f)
            self.ids = js["0"]
            self.ids += js["1"]
            self.ids += js["2"]
            self.ids += js["4"]

        self.pack_size = self.environment.parsed_options.tags_in_pack

        self.ws = websocket.WebSocket()
        self.ws.settimeout(10)
        self.ws.connect(self.host)

        self.start_date = datetime.utcfromtimestamp(1690454451).date()
        self.end_date = datetime.utcfromtimestamp(1690971801).date() - timedelta(days=1)
        """
        with open("/mnt/locust/tags_in_postgres.json", "r") as f:
            js = json.load(f)
            self.ids = js["0"]
            '''
            self.ids += js["1"]
            self.ids += js["2"]
            self.ids += js["4"]
            '''

        self.ws = websocket.WebSocket()
        self.ws.settimeout(10)
        self.ws.connect(self.host)

        self.pack_size = self.environment.parsed_options.tags_in_pack
        self.start_date = self.environment.parsed_options.start
        self.end_date = self.environment.parsed_options.finish

        self.payload = {
            "action": "get",
            "data": {}
        }
        if self.start_date:
            self.payload["data"]["start"] = times.ts(self.start_date)
        self.end_date = self.environment.parsed_options.finish
        if self.end_date:
            self.payload["data"]["finish"] = times.ts(self.end_date)

    @task
    def get_data(self):
        self.payload["data"]["tagId"] = random.sample(self.ids, self.pack_size)

        e = None
        try:
            json_data = json.dumps(self.payload)

            start_time = time.time()

            g = gevent.spawn(self.ws.send, json_data)
            g.get(block=True, timeout=2)

            g = gevent.spawn(self.ws.recv)
            res = g.get(block=True, timeout=10)
        except Exception as exp:
            e = exp
            self.ws.close()
            print("Ошибка!")
            time.sleep(2)
            self.ws.connect(self.host)

        elapsed = int((time.time() - start_time) * 1000)
        events.request.fire(
            request_type='ws', name=self.host,
            response_time=elapsed,
            response_length=0, exception=e
        )

    def on_close(self):
        self.ws.close()
