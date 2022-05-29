# простой тестовый скрипт для записи данных в Victoriametrics
# принимает в качестве аргументов:
# 1. h=<server_name_or_ip_with_port> - адрес сервера (по умолчанию - localhost:4242)
# 2. m=<metric_name> - имя метрики (по умолчанию - temp)
# 3. f=<frequency> - частота записи данных в секундах (по умолчанию - 2)
# с указанной частотой записывает случайное значение метрики
# в диапазоне от -10 до 10

import sys

import logging
import requests

from random import randint
from time import sleep

def main(args):
    url = 'http://{}/api/put'.format(args["h"])
    payload = {}
    payload["metric"] = args["m"]

    try:
        while True:
            val = randint(-10, 10)
            payload["value"] = val
            r = requests.post(url, json=payload)
            print("Value: {}; Status: {}".format(val, r.status_code))
            sleep(args["f"])

    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == '__main__':
    print("Тестовый скрипт записи данных в TSDB по протоколу HTTP OpenTSDB.")
    print("Запуск: python3 test_writer.py h=<server> m=<metric_name> f=<frequency>.")
    print("Значения по умолчанию: h=localhost:4242 m=temp f=2.")
    print("Порядок аргументов не важен.")

    logging.basicConfig(level=logging.DEBUG)

    args = sys.argv[1:]

    dict_args = dict(s.split('=') for s in args)
    dict_args.setdefault("h", "localhost:4242")
    dict_args.setdefault("m", "temp")
    dict_args.setdefault("f", 2)
    dict_args["f"] = int(dict_args["f"])

    main(dict_args)
