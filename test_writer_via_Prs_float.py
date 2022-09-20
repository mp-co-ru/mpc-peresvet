# простой тестовый скрипт для записи вещественных данных в Peresvet
# принимает в качестве аргументов:
# 1. h=<server_name_or_ip_with_port> - адрес сервера (по умолчанию - localhost:8002)
# 2. t=<tag_id> - id тэга
# 3. f=<frequency> - частота записи данных в секундах (по умолчанию - 2)
# с указанной частотой записывает случайное значение метрики
# в диапазоне от -10 до 10

import sys

import logging
from random import random
from time import sleep
import requests

def main(args):
    url = f'http://{args["h"]}/data'
    payload = {"data": [
        {
            "tagId": args["t"],
            "data": [
                {
                    "y": None
                }
            ]
        }
    ]}

    try:
        while True:
            val = (random() - 0.5) * 20
            payload["data"][0]["data"][0]["y"] = val
            r = requests.post(url, json=payload)
            print(f"Value: {val}; Status: {r.status_code}")
            sleep(args["f"])

    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == '__main__':
    print("Тестовый скрипт записи данных в TSDB по протоколу HTTP OpenTSDB.")
    print("Запуск: python3 test_writer.py h=<server> t=<tagId> f=<frequency>.")
    print("Значения по умолчанию: h=localhost:8002 f=2.")
    print("Порядок аргументов не важен.")

    logging.basicConfig(level=logging.DEBUG)

    args = sys.argv[1:]

    dict_args = dict(s.split('=') for s in args)
    dict_args.setdefault("h", "localhost:8002")
    dict_args.setdefault("f", 2)
    dict_args["f"] = int(dict_args["f"])

    main(dict_args)
