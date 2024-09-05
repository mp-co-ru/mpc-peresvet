"""
Запросы на создание, чтение, обновление, удаление тревог.
"""
import sys
from pydantic import Field
from fastapi import APIRouter, Depends

sys.path.append(".")

from src.common import api_crud_svc as svc
from src.services.alerts.api_crud.alerts_api_crud_settings import AlertsAPICRUDSettings

class AlertCreateAttributes(svc.NodeAttributes):
    """При создании тревоги атрибут ``prsJsonConfigString`` имеет формат

    .. code:: python

        {
            # "тревожное" значение тега
            "value": ...
            # способ сравнения значения тега с "тревожным":
            # если high = true, то тревога возникает, если значение тега >= value
            # иначе - значение тега < value
            "high": true
            # флаг автоквитирования
            "autoAck": true
        }

    Args:
        svc (_type_): _description_
    """
    pass

class AlertCreate(svc.NodeCreate):
    attributes: AlertCreateAttributes = Field({}, title="Атрибуты тревоги")

class AlertRead(svc.NodeRead):
    pass

class AlertUpdate(svc.NodeUpdate):
    pass

class AlertsAPICRUD(svc.APICRUDSvc):
    """Сервис работы с тегами в иерархии.

    Подписывается на очередь ``tags_api_crud`` обменника ``tags_api_crud``,
    в которую публикует сообщения сервис ``tags_api_crud`` (все имена
    указываются в переменных окружения).

    Формат ожидаемых сообщений

    """

    _outgoing_commands = {
        "create": "alerts.create",
        "read": "alerts.read",
        "update": "alerts.update",
        "delete": "alerts.delete"
    }

    def __init__(self, settings: AlertsAPICRUDSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def create(self, payload: AlertCreate) -> dict:
        return await super().create(payload=payload)

    async def read(self, payload: AlertRead) -> dict:
        return await super().read(payload=payload)

    async def update(self, payload: AlertUpdate) -> dict:
        return await super().update(payload=payload)

settings = AlertsAPICRUDSettings()

app = AlertsAPICRUD(settings=settings, title="`AlertsAPICRUD` service")

router = APIRouter(prefix=f"{settings.api_version}/alerts")

error_handler = svc.ErrorHandler()

@router.post("/", response_model=svc.NodeCreateResult, status_code=201)
async def create(payload: AlertCreate, error_handler: svc.ErrorHandler = Depends()):
    """
    Метод добавляет тревогу в модель.

    **Запрос:**

        .. http:example::
            :request: ../../../../docs/source/samples/alerts/addAlertIn.txt
            :response: ../../../../docs/source/samples/alerts/addAlertOut.txt

        * **parentId** (str) - id тега, к которому привязывается тревога. Обязательный атрибут.
        * **attributes** (dict) - параметры создаваемой тревоги. Необязательное поле.

          * **cn** (str) - имя тревоги. Необязательный атрибут.
          * **description** (str) - описание тревоги. Необязательный атрибут.
          * **prsJsonConfigString** (str) - Строка содержит, в случае необходимости,
            конфигурацию тревоги. 
            При создании тревоги атрибут ``prsJsonConfigString`` имеет формат:

            .. code:: python

                {
                    # "тревожное" значение тега
                    "value": 0,
                    # способ сравнения значения тега с "тревожным":
                    # если high = true, то тревога возникает, если значение тега >= value
                    # иначе - значение тега < value
                    "high": True,
                    # флаг автоквитирования
                    "autoAck": True
                }
            
            Обязательный аттрибут.
          * **prsActive** (bool) - Определяет, активна ли тревога. По умолчанию = ``true``.
            Необязательный атрибут.
          * **prsIndex** (int) - Если у узлов одного уровня иерархии проставлены индексы, то
            перед отдачей клиенту списка экземпляров они сортируются в соответствии
            с их индексами. Необязательный атрибут.

    **Ответ:**

        * **id** (str) - идентификатор созданной тревоги.
        * **detail** (str) - пояснение к возникшей ошибке.

    """

    res = await app.create(payload)
    await error_handler.handle_error(res)
    return res

@router.get("/", response_model=svc.NodeReadResult | None, status_code=200)
async def read(q: str | None = None, payload: AlertRead | None = None, error_handler: svc.ErrorHandler = Depends()):
    """
    Метод ищет тревоги в модели и возвращает запрошенные по ним данные.

    **Пример запроса в формате JSON.**

    .. http:example::
       :request: ../../../../docs/source/samples/alerts/getAlertsIn.txt
       :response: ../../../../docs/source/samples/alerts/getAlertsOut.txt

    **Пример query запроса.**

    .. http:example::
       :request: ../../../../docs/source/samples/alerts/getAlertsIn_query.txt
       :response: ../../../../docs/source/samples/alerts/getAlertsOut.txt

    **Параметры запроса:**

       * **id** (str | list(str)) - идентификатор тревоги (тревог), данные о которой(-ых) хотим прочитать. 
         Необязательный атрибут.
       * **base** (str) - Базовый узел для поиска. В случае отсутствия поиск проводится по всей модели.
         Необязательный атрибут.
       * **deref** (bool) - Флаг разыменования ссылок. По умолчанию true. Необязательный атрибут.
       * **scope** (int) - Масштаб поиска. По умолчанию 1.\n
         0 - получение данных по указанному в ключе ``base`` узлу \n
         1 - поиск среди непосредственных потомков указанного в ``base`` узла\n
         2 - поиск по всему дереву, начиная с указанного в ``base`` узла.\n
         Необязательный атрибут.
       * **filter** (dict) - Словарь из атрибутов и их значений, из которых
         формируется фильтр для поиска. В случае отсутствия возвращаются все тревоги, 
         найденные под узлом, указанным в атрибуте ``base``. 
         При формировании фильтра значения ключей объединяются логической операцией ``ИЛИ``, а сами
         ключи - операцией ``И``.
         При указании значения строкового атрибута можно использовать символ маски ``*``.
         Пример фильтра:

         .. code:: json

            {
                "cn": ["alert*"],
                "prsActive": [true],
                "prsIndex": [1, 2, 3]
            } 

         Данный фильтр вернёт тревоги, у которых:\n
         (Имя начинается с ``alert``) И (флаг активности = ``true``) И (индекс равен 1 ИЛИ 2 ИЛИ 3).

       * **attributes** (list[str]) - Список атрибутов, значения которых необходимо вернуть в ответе. По умолчанию - ['\*'], то есть все атрибуты (кроме системных).

    **Ответ:**

        * **data** (list) - найденные тревоги с их параметрами.
        * **detail** (str) - пояснение к возникшей ошибке.

    """

    res = await app.api_get_read(AlertRead, q, payload)
    await error_handler.handle_error(res)
    return res

@router.put("/", status_code=202)
async def update(payload: AlertUpdate, error_handler: svc.ErrorHandler = Depends()):
    """
    Метод обновляет тревогу в модели.

    **Запрос:**

        .. http:example::
            :request: ../../../../docs/source/samples/alerts/putAlertIn.txt
            :response: ../../../../docs/source/samples/alerts/putAlertOut.txt

        * **id** (str) - id тревоги для обновления. Обязательное поле.
        * **attributes** (dict) - словарь с параметрами для обновления.
          Соответствует атрибутам из команды ``create``.
          

    **Ответ:**

        * {} - пустой словарь в случае успешного запроса.
        * **detail** (list) - список с пояснениями к ошибке.

    """
    res = await app.update(payload)
    await error_handler.handle_error(res)
    return res

@router.delete("/", status_code=202)
async def delete(payload: svc.NodeDelete, error_handler: svc.ErrorHandler = Depends()):
    """
    Метод удаляет тревогу из иерархии.

    **Запрос:**

        .. http:example::
            :request: ../../../../docs/source/samples/alerts/deleteAlertIn.txt
            :response: ../../../../docs/source/samples/alerts/deleteAlertOut.txt

        * **id** (str | [str]) - id или список id тревоги (тревог) для удаления. Обязательное поле.

    **Ответ:**

        * null - в случае успешного запроса
        * **detail** (list) - список с пояснениями к ошибке

    """
    res = await app.delete(payload)
    await error_handler.handle_error(res)
    return res

app.include_router(router, tags=["alerts"])
