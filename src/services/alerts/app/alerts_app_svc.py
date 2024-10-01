"""
Модуль содержит классы, описывающие входные данные для команд CRUD для тегов
и класс сервиса ``tags_api_crud_svc``\.
"""
import sys
import copy
import json
import hashlib
from ldap.dn import str2dn, dn2str

sys.path.append(".")

from src.common.app_svc import AppSvc
from src.services.alerts.app.alerts_app_settings import AlertsAppSettings
from src.common.hierarchy import CN_SCOPE_ONELEVEL, CN_SCOPE_SUBTREE

class AlertsApp(AppSvc):
    """Сервис работы с тревогами.
    """

    def __init__(self, settings: AlertsAppSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    def _add_app_handlers(self):
        self._handlers[f"{self._config.hierarchy['class']}.app_api.get_alarms"] = self._get_alarms
        self._handlers[f"{self._config.hierarchy['class']}.app_api.ack_alarm"] = self._ack_alarm
        self._handlers["prsTag.app.data_set.*"] = self._tag_value_changed
        self._handlers["prsTag.model.deleteing.*"] = self._tag_deleting

    async def _tag_deleting(self, mes):
        payload = {
            "base": mes['id'],
            "scope": CN_SCOPE_SUBTREE, # по идее, у тега могут быть только тревоги и методы, то есть уровень ниже, но - на всякий случай
            "filter": {
                "objectClass": ["prsAlert"]
            },
            "attributes": ["cn"]
        }
        alerts = await self._hierarchy.search(payload=payload)
        for alert in alerts:
            self._delete_alert_cache(alert[0])
        
        await self._amqp_consume_queue.unbind(f"prsTag.model.deleteing.{mes['id']}")
        await self._amqp_consume_queue.unbind(f"prsTag.app.data_set.{mes['id']}")

    async def _created(self, mes):
        # тревога создана
        await self._get_alert(mes['id'])

    async def _updated(self, mes):
        # метод, срабатывающий на изменение экземпляра сущности в иерархии
        # сервис <>.app подписан на это событие по умолчанию

        # поступаем так: удаляем кэш
        # читаем данные по тревоге

        #TODO: не учитываем пока возможности переноса тревоги на другого родителя!

        await self._make_alert_cache(mes["id"])
    
    async def _deleted(self, mes):
        await self._delete_alert_cache(mes["id"])

    async def _delete_alert_cache(self, alert_id: str):
        await self._cache.delete(f"{alert_id}.{self._config.svc_name}").exec()

    async def _make_alert_cache(self, tag_id: str):
        await self._delete_alert_cache(tag_id=tag_id)

        res = await self._hierarchy.search({
            "id": tag_id,
            "attributes": ["prsActive"]
        })
        if not res:
            return False
        
        active = res[0][2]["prsActive"][0] == 'TRUE'
        res = await self._cache.set(name=f"{tag_id}.{self._config.svc_name}", obj={"prsActive": active}).exec()
        return res[0]

    async def _get_alarms(self, mes: dict) -> dict:
        """_summary_

        Args:
            

        Returns:
            dict: _description_
        """
        get_alerts = {
            "base": await self._hierarchy.get_node_id(self._cache._cache_node_dn),
            "scope": CN_SCOPE_ONELEVEL,
            "filter": {
                "cn": ['*.alerts_app']
            },
            "attributes": ["prsJsonConfigString"]
        }
        alerts = await self._hierarchy.search(get_alerts)
        result = {
            "data": []
        }
        for alert in alerts:
            a_data = json.loads(alert[2]["prsJsonConfigString"][0])
            if a_data["fired"]:
                result["data"].append({
                    "alertId": alert[0],
                    "fired": a_data["fired"],
                    "acked": a_data["acked"]
                })

        return result

    async def _ack_alarm(self, mes: dict):
        """_summary_

        Args:
            mes (dict): {
                "id": "alert_id",
                "x": 123                
            }
        """
        alert_id = mes["id"]
        alert_cache_key = f"{alert_id}.{self._config.svc_name}"
        alert_data = await self._cache.get(name=alert_cache_key).exec()

        if not alert_data[0]:
            self._logger.error(f"{self._config.svc_name} :: Отсутствует кэш по тревоге {alert_id}.")
            return

        if not alert_data[0]["fired"]:
            self._logger.warning(f"{self._config.svc_name} :: Тревога {alert_id} неактивна.")
            return

        if alert_data[0]["acked"]:
            self._logger.warning(f"{self._config.svc_name} :: Тревога {alert_id} уже квитирована.")
            return

        alert_data[0]["acked"] = mes["x"]
        await self._cache.set(name=alert_cache_key, obj=alert_data)
        await self._post_message(
            {
                "alertId": alert_id,
                "x": mes["data"]["x"]                
            },
            reply=False,
            routing_key=f"{self._config.svc_name}.alarm_acked.{alert_id}"
        )

    async def _tag_value_changed(self, mes: dict) -> None:
        """_summary_

        Args:
            mes (dict): {
                "data": {
                    "data": [
                        {
                            "tagId": "...",
                            "data": [
                                (1, 2, 3)
                            ]
                        }
                    ]
                }
            }
        """
        for tag_item in mes["data"]["data"]:
            tag_id = tag_item["tagId"]

            get_alerts = {
                "base": tag_id,
                "scope": CN_SCOPE_ONELEVEL,
                "filter": {
                    "objectClass": ["prsAlert"],
                    "prsActive": [True]
                },
                "attributes": ["entryUUID"]
            }
            alerts = await self._hierarchy.search(get_alerts)
            for alert in alerts:
                alert_id = alert[0]
                alert_data = await self._cache.get(
                    f"{alert_id}.{self._config.svc_name}"
                ).exec()

                if not alert_data[0]:
                    self._logger.error(f"Нет кэша тревоги {alert_id}.")
                    continue

                for data_item in tag_item["data"]:

                    # если данные более ранние, чем уже обработанные...
                    if alert_data[0]["fired"]:
                        if data_item[1] <= alert_data[0]["fired"]:
                            continue
                        if alert_data[0]["acked"] and (data_item[1] <= alert_data[0]["acked"]):
                            continue

                    alert_on = (
                        data_item[0] < alert_data[0]["value"],
                        data_item[0] >= alert_data[0]["value"],
                    )[alert_data[0]["high"]]

                    self._logger.debug(f"Alarm on: {alert_on}")

                    if (alert_data[0]["fired"] and alert_on) or \
                        (not alert_data[0]["fired"] and not alert_on):
                        continue

                    if not alert_data[0]["fired"] and alert_on:
                        await self._post_message(
                            {                                
                                "alertId": alert_id,
                                "x": data_item[1]
                            },
                            reply=False,
                            routing_key=f"{self._config.svc_name}.alarm_on.{alert_id}"
                        )
                        alert_data[0]["fired"] = data_item[1]

                        if alert_data[0]["autoAck"]:
                            await self._post_message(
                                {                                    
                                    "alertId": alert_id,
                                    "x": data_item[1]                                    
                                },
                                reply=False,
                                routing_key=f"{self._config.svc_name}.alarm_acked.{alert_id}"
                            )
                            alert_data[0]["acked"] = data_item[1]


                    if alert_data[0]["fired"] and not alert_on:
                        await self._post_message(
                            {
                                "alertId": alert_id,
                                "x": data_item[1]                             
                            },
                            reply=False,
                            routing_key=f"{self._config.svc_name}.alarm_off.{alert_id}"
                        )
                        alert_data[0]["fired"] = None
                        alert_data[0]["acked"] = None

                await self._cache.set(
                    name=f"{alert_id}.{self._config.svc_name}",
                    obj=alert_data
                ).exec()

    def _cache_key(self, *args):
        '''
        return hashlib.sha3_256(
            f"{'.'.join(args)}".encode()
        ).hexdigest()   # SHA3-256
        '''
        return f"{'.'.join(args)}"
    
    async def _get_alert(self, alert_id) -> None:
        payload = {
            "id": alert_id,
            "attributes": ['prsActive', 'cn', 'description', 'prsJsonConfigString']
        }
        alert_data = await self._hierarchy.search((payload))
        if not alert_data:
            self._logger.error(f"{self._config.svc_name} :: Нет данных по тревоге {alert_id}")
            return
        alert = alert_data[0]

        active = alert[2]["prsActive"][0] == 'TRUE'
        if not active:
            self._logger.warning(f"{self._config.svc_name} :: Тревога {alert_id} неактивна.")
            return

        try:
            # json.loads вполне может возвращать целые и вещественные числа,
            # то есть преобразует строку не только в словарь, но и в другие типы
            alert_config = json.loads(alert[2]["prsJsonConfigString"][0])
        except (json.JSONDecodeError, TypeError):
            alert_config = None

        if not isinstance(alert_config, dict):
            self._logger.error(f"{self._config.svc_name} :: У тревоги '{alert_id}' неверная конфигурация.")
            self._delete_alert_cache(alert_id=alert_id)
            return

        tag_id, _ = await self._hierarchy.get_parent(alert_id)

        alert_data = {
            #"tagId": tag_id,
            "alertId": alert_id,
            "fired": False,
            "acked": False,
            "value": alert_config["value"],
            "high": alert_config["high"],
            "autoAck": alert_config["autoAck"],
            "cn": alert[2]["cn"][0],
            "description": alert[2]["description"][0]
        }

        await self._cache.set(
            name=f"{alert_id}.{self._config.svc_name}",
            obj=alert_data
        ).exec()

        # проведём активацию тревоги ---------------
        payload = {
            "tagId": tag_id
        }
        res = await self._post_message(
            mes=payload, 
            reply=True, 
            routing_key="prsTag.app_api_client.get_data"
        )
        if res.get('data'):
            await self._tag_value_changed(res)
            
        # -----------------------------------------

        # подпишемся на события изменения значений тега
        await self._amqp_consume_queue.bind(
            exchange=self._exchange,
            routing_key=f"tags.app.data_set.{tag_id}"
        )
        await self._amqp_consume_queue.bind(
            exchange=self._exchange,
            routing_key=f"prsTag.model.deleting.{tag_id}"
        )
        
        self._logger.debug(f"{self._config.svc_name} :: Тревога {alert_id} прочитана.")

    async def _get_alerts(self) -> None:
        get_alerts = {
            "filter": {
                "objectClass": ["prsAlert"],
                "prsActive": [True]
            },
            "attributes": ["cn", "description", "prsJsonConfigString"]
        }
        alerts = await self._hierarchy.search(get_alerts)
        for alert in alerts:
            await self._get_alert(alert[0])

    async def on_startup(self) -> None:
        await super().on_startup()

        # по умолчанию очередь привязывается к изменениям всех тегов
        # нам же нужны только изменения тегов, у которых есть тревоги
        await self._amqp_consume_queue.unbind(self._exchange, "prsTag.app.data_set.*")
        # будем подписываться на удаление только тех тегов, к которым привязаны алерты
        await self._amqp_consume_queue.unbind(self._exchange, "prsTag.model.deleting.*")

        try:
            await self._get_alerts()
        except Exception as ex:
            self._logger.error(f"Ошибка чтения тревог: {ex}")

settings = AlertsAppSettings()

app = AlertsApp(settings=settings, title="`TagsApp` service")
