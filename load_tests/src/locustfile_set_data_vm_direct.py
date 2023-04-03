import json
import random
import string
from uuid import uuid4

from locust import HttpUser, TaskSet, task, between, events

class DataSetUser(HttpUser):

    @task
    def set_json_data(self):
        metric_name = random.choice(self.metric_names)
        metric_area_tag = random.choice(self.metric_tags['area'])
        self.client.post("http://vm:4242/api/put", 
        json={
            "metric": metric_name,
            "tags": {
                "workshop": "Main", "area": metric_area_tag, "machine": "AC_CLASSIC_V2_13"
            },
            "value": random.uniform(-100, 100)
        }
        )
    
    def on_start(self):
        with open("/mnt/locust/vm_metrics.json", "r") as f:
            self.metrics = json.load(f)
            self.metric_names = self.metrics['metric']
            self.metric_tags = self.metrics['tags']
