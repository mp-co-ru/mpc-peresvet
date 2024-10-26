
# Модуль чтения исторических данных.
# Протокол - WebSocket.
# Период и количество тегов в запросе задаётся в окне создания запроса.
# База данных - postgresql или victoriametrics.

import json
import random
import websocket
import gevent

from locust import User, task, events

import time

from uuid import uuid4

#from locust_plugins.users import SocketIOUser

class WSDataGetHistoryUser(User):

    def on_start(self):
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

        self.start_date = self.environment.parsed_options.start
        self.end_date = self.environment.parsed_options.finish

    @task
    def get_data(self):
        tags = random.sample(self.ids, self.pack_size)

        delta = self.end_date - self.start_date
        random_date = self.start_date + timedelta(days=random.randint(0, delta.days))
        start = random_date.isoformat()
        end = (random_date + timedelta(days=1)).isoformat()

        data = {
        "action": "get",
        "data": {
        "tagId": tags,
        "start": start,
        "finish": end
        }
        }

        e = None
        try:
            json_data = json.dumps(data)

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
