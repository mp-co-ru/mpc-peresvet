import json
import random
import string
from uuid import uuid4

from locust import HttpUser, TaskSet, task, between, events


class DataGetUser(HttpUser):

    def on_start(self):
        self.time_interval = [1680514064, 1680514661]
        with open("/mnt/locust/vm_metrics.json", "r") as f:
            self.metrics = json.load(f)
            self.metric_names = self.metrics['metric']
            self.metric_tags = self.metrics['tags']


    @task
    def get_metric_data(self):
        metric_name = random.choice(self.metric_names)
        metric_area_tag = random.choice([tag['area'] for tag in self.metric_tags])
        params_string = "?query={{__name__='{metric_name}',area='{metric_area_tag}'}}&start=1680514064&end=1680514661&step=0.2s".format(
            metric_name=metric_name,
            metric_area_tag=metric_area_tag
            )
        self.client.get("http://vm:8428/api/v1/query_range"+params_string)

    @task
    def get_aggregated_metric_data(self):
        # time_interval = 
        metric_name = random.choice(self.metric_names)
        metric_area_tag = random.choice([tag['area'] for tag in self.metric_tags])
        params_string = "?query=avg_over_time({{__name__='{metric_name}',area='{metric_area_tag}'}})&start=1680514064&end=1680514661&step=0.2s".format(
            metric_name=metric_name,
            metric_area_tag=metric_area_tag
            )
        self.client.get("http://vm:8428/api/v1/query_range"+params_string)

    @task
    def get_one_metric_value(self):
        metric_name = random.choice(self.metric_names)
        metric_area_tag = random.choice([tag['area'] for tag in self.metric_tags])
        timestamp = random.randint(self.time_interval[0], self.time_interval[1])
        params_string = "?query={{__name__='{metric_name}',area='{metric_area_tag}'}}@{timestamp}".format(
            metric_name=metric_name,
            metric_area_tag=metric_area_tag,
            timestamp=timestamp
        )
        self.client.get("http://vm:8428/api/v1/query"+params_string)

