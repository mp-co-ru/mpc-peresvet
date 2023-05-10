"""
Модуль, содержащий базовый класс для управления экземплярами сущностей
в иерархии. По умолчанию, каждая сущность может иметь свой узел в иерархрии
для создания в нём своей иерархии, но это необязательно.
К примеру, наиболее используемая иерархия создаётся в узле ``objects``,
которым управляет сервис ``objects_model_crud_svc``.
"""

from typing import Annotated, Any, List
import asyncio
import json

import aio_pika
import aio_pika.abc

from hierarchy import CN_SCOPE_ONELEVEL, CN_SCOPE_SUBTREE
from src.common.svc import Svc
from src.common.model_crud_settings import ModelCRUDSettings

class ModelCRUDSvc(Svc):
    """Базовый класс для всех сервисов, работающих с экземплярами сущностей
    в иерархической модели.

    При запуске подписывается на сообщения
    обменника с именем, задаваемым в переменной ``api_crud_exchange``,
    создавая очередь с именем из переменной ``api_crud_queue``.

    Сообщения, приходящие в эту очередь, создаются сервисом API_CRUD.
    Часть сообщений эмулируют RPC, у них параметр ``reply_to`` содержит имя
    очереди, в которую нужно отдать результат.
    Это сообщения: создание, поиск. Другие же сообщения (update, delete)
    не предполагают ответа.

    Args:
        settings (ModelCRUDSettings): конфигурация сервиса.

    """

    def __init__(self, settings: ModelCRUDSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

        self._api_crud_exchange_name : str = settings.api_crud_exchange
        self._api_crud_queue_name : str = settings.api_crud_queue

        self._hierarchy_node : str = settings.hierarchy_node
        self._hierarchy_class : str = settings.hierarchy_class
        self._hierarchy_parent_classes = []
        if settings.hierarchy_parent_classes:
            classes = settings.hierarchy_parent_classes.split(",")
            self._hierarchy_parent_classes = [
                object_class.strip() for object_class in classes
            ]

        self._svc_consume_channel: aio_pika.abc.AbstractRobustChannel = None
        self._svc_consume_exchange: aio_pika.abc.AbstractRobustExchange = None
        self._svc_consume_queue: aio_pika.abc.AbstractRobustQueue = None

    async def _amqp_connect(self) -> None:
        """Связь с amqp-сервером.
        В дополнение к обменнику, создаваемому классом-предком
        :class:`svc.Svc`, в этом методе
        создаётся обменник и очередь для получения сообщений от сервиса
        ``<сущность>_api_crud_svc``.

        """
        await super()._amqp_connect()

        self._svc_consume_channel = await self._amqp_connection.channel()
        self._svc_consume_exchange = await self._svc_consume_channel.declare_exchange(
            self._api_crud_exchange_name, aio_pika.ExchangeType.FANOUT,
        )
        self._svc_consume_queue = await self._svc_consume_channel.declare_queue(
            self._api_crud_queue_name, durable=True
        )
        await self._svc_consume_queue.bind(exchange=self._svc_consume_exchange)
        await self._svc_consume_queue.consume(self._process_message)
        await asyncio.Future()

    async def _process_message(self,
            message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        """Метод обработки сообщений от сервиса ``<сущность>_api_crud_svc``.

        Сообщения должны приходить в формате:

        .. code:: json

            {
                "action": "create/read/update/delete",
                "data: {}
            }

        где

        * **action** - команда ("create", "read", "update", "delete"), при
          этом строчные или прописные буквы - не важно;
        * **data** - параметры команды.

        После выполнения соответствующей команды входное сообщение квитируется
        (``messsage.ack()``).

        В случае, если в сообщении установлен параметр ``reply_to``,
        то квитирование происходит после публикации ответного сообщения в
        очередь, указанную в ``reply_to``.

        """
        async with message.process(ignore_processed=True):
            mes = message.body.decode()
            try:
                mes = json.loads(mes)
            except json.decoder.JSONDecodeError:
                self._logger.error(f"Сообщение {mes} не в формате json.")
                await message.ack()
                return

            action = mes.get("action")
            if not action:
                self._logger.error(f"В сообщении {mes} не указано действие.")
                await message.ack()
                return

            action = action.lower()
            if action == "create":
                res = await self._create(mes)
            elif action == "update":
                res = await self._update(mes)
            elif action == "read":
                res = await self._read(mes)
            elif action == "delete":
                res = await self._delete(mes)
            else:
                self._logger.error(f"Неизвестное действие: {action}.")
                await message.ack()
                return

            if not message.reply_to:
                await message.ack()
                return

            await self._svc_consume_exchange.publish(
                aio_pika.Message(
                    body=res,
                    correlation_id=message.correlation_id,
                ),
                routing_key=message.reply_to,
            )
            await message.ack()

    async def _update(self, data: dict) -> None:
        """Метод обновления данных узла. Также метод может перемещать узел
        по иерархии.

        Args:
            data (dict): данные узла.
        """

        new_parent = data.get("parentId")
        if new_parent:
            if self._check_parent_class(new_parent):
                self._hierarchy.move(data['id'], new_parent)
            else:
                self._logger.error("Неправильный класс нового родительского узла.")
                return

        self._hierarchy.modify(data["id"], data["attributes"])
        self._updating(data)
        await self._svc_pub_exchange.publish(
            aio_pika.Message(
                body=f'{{"action": "updated", "id": {data["id"]}}}'.encode(),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="*"
        )
        self._logger.info(f'Узел {data["id"]} обновлён.')

    async def _updating(self, data: dict) -> None:
        """Метод переопределяется в сервисах-наследниках.
        В этом методе содержится специфическая работа при обновлении
        нового экземпляра сущности.
        Метод вызывается методом ``update`` после изменения узла в иерархии,
        но перед посылкой сообщения об изменении в очередь.

        Args:
            data (dict): id и атрибуты вновь создаваемого экземпляра сущности
        """

    async def _delete(self, ids: List[str]) -> None:
        """Метод удаляет экземпляр сущности из иерархии.

        Args:
            ids (List[str]): список идентификаторов узлов
        """
        for node in ids:
            self._hierarchy.delete(node)

        await self._svc_pub_exchange.publish(
            aio_pika.Message(
                body=f'{{"action": "deleted", "id": {ids}}}'.encode(),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="*"
        )
        self._logger.info(f'Узлы {ids} удалены.')

    async def _deleting(self, ids: List[str]) -> None:
        """Метод переопределяется в сервисах-наследниках.
        Используется для выполнения специфической работы при удалении
        экземпляра сущности.

        Вызывается методом ``delete`` после удаления узла в иерархии, но
        перед посылкой сообщения об удалении в очередь.

        Args:
            ids (List[str]): список ``id`` удаляемых узлов.
        """

    async def _read(
        self, base: str = None,
        filter_str: str = None,
        scope: Any = CN_SCOPE_SUBTREE,
        attr_list: list[str] = None) -> List[tuple]:
        """Метод поиска узлов и чтения их данных.

        Args:
            * base (str, optional): Базовый узел для поиска.
              В случае отсутствия поиск ведётся от вершины всей иерархии.
            * filter_str (str, optional): Фильтр поиска.
            * scope (Any, optional): Уровень поиска:
              0 - используется для чтения параметров одного узла;
              1 - поиск среди непосредственных потомков узла;
              2 - поиск по всему дереву.
            * attr_list (list[str], optional): Список атрибутов для возврата.

        Returns:
            List[Tuple]: [(id, dn, attrs), ...]
        """
        return self._hierarchy.search(
            base=base, filter_str=filter_str, scope=scope, attr_list=attr_list
        )

    async def _create(self, data: dict) -> dict:
        """Метод создаёт новый экземпляр сущности в иерархии.

        Args:
            data (dict): входные данные вида:

                .. code-block:: json

                    {
                        "parentId": "id родителя",
                        "attributes": {
                            "ldap-attribute": "value"
                        }
                    }

                ``parentId`` - id родительской сущности; в случае, если = None,
                то экзмепляр создаётся внутри базового для данной сущности
                узла; если ``parentId`` = None и нет базового узла, то
                генерируется ошибка.

        Returns:
            dict: {"id": "new_id"}

        """

        parent_node = data.get("parentId")
        parent_node = parent_node if parent_node else self._hierarchy_node
        if not parent_node:
            res = {
                "id": None,
                "error": {
                    "code": 406,
                    "message": "Не указан родительский узел."
                }
            }
            return res

        if not self._check_parent_class(data["parentId"]):
            res = {
                "id": None,
                "error": {
                    "code": 406,
                    "message": "Неприемлемый класс родительского узла."
                }
            }
            return res

        new_id = self._hierarchy.add(parent_node, data.get("attributes"))

        if not new_id:
            res = {
                "id": None,
                "error": {
                    "code": 406,
                    "message": "Ошибка создания узла."
                }
            }
        else:
            res = {
                "id": new_id,
                "error": {}
            }

        await self._creating(data, new_id)

        await self._svc_pub_exchange.publish(
            aio_pika.Message(
                body=f'{{"action": "created", "id": {new_id}}}'.encode(),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key="*"
        )

        return res

    async def _creating(self, data: dict, new_id: str) -> None:
        """Метод переопределяется в сервисах-наследниках.
        В этом методе содержится специфическая работа при создании
        нового экземпляра сущности.

        Метод вызывается методом ``create`` после создания узла в иерархии,
        но перед посылкой сообщения о создании в очередь.

        Args:
            data (dict): атрибуты вновь создаваемого экземпляра сущности;

            new_id (str): id уже созданного узла
        """

    async def _check_parent_class(self, parent_id: str) -> bool:
        """Метод проверки того, что класс родительского узла
        соответсвует необходимому. К примеру, тревоги могут создаваться только
        внутри тегов. То есть при создании новой тревоги мы должны убедиться,
        что класс родительского узла - ``prsTag``.

        Список всех возможных классов узлов-родителей указывается
        в конфигурации в переменной ``hierarchy_parent_classes``.

        Args:
            parent_id (str): идентификатор родительского узла

        Returns:
            bool: True | False
        """
        if self._hierarchy_parent_classes:
            if (self._hierarchy.get_node_class(parent_id) in
                self._hierarchy_parent_classes):
                return True

        return False

    async def _update(self, data: dict) -> None:
        """Метод обновляет узел в иерархии.

        В случае, если в ``data`` есть ключ ``parentId``, то узел будет
        перемещён по иерархии. При этом если ``parentId == None``, то узел
        будет перемещён в базовый узел сущности.

        Пример: допустим, мы изменяем тег, принадлежащий объекту и в параметрах
        команды ``update`` указываем ``parentId = None``. В этом случае тег
        будет перемещён из-под узла объекта в базовый узел сущности тег:
        ``cn=tags,cn=prs``.

        Args:
            data (dict): новые параметры узла.
        """
        await self._hierarchy.modify(data["id"], data["attributes"])

    async def _check_hierarchy_node(self) -> None:
        """Метод проверяет наличие базового узла сущности и, в случае его
        отсутствия, создаёт его.
        """
        if not self._hierarchy_node:
            return

        item = await self._hierarchy.search(scope=CN_SCOPE_ONELEVEL, filter_str=f"(cn={self._hierarchy_node})", attr_list=["entryUUID"])
        if item:
            return

        await self._hierarchy.add(attr_vals={"cn": self._hierarchy_node})

    async def on_startup(self) -> None:
        """Метод, выполняемый при старте приложения:
        происходит проверка базового узла сущности.
        :py:func:`model_crud_svc.ModelCRUDSvc._check_hierarchy_node`
        """
        await super().on_startup()
        await self._check_hierarchy_node()
