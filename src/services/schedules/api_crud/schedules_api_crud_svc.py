"""
Модуль содержит примеры запросов и ответов на них, параметров которые могут входить в
запрос, в сервисе schedules.
"""
from copy import deepcopy
import sys
import json
from typing import List
from pydantic import Field, validator

from fastapi import APIRouter, Depends

sys.path.append(".")

from src.common import api_crud_svc as svc
from src.common import times as t
from src.services.schedules.api_crud.schedules_api_crud_settings import SchedulesAPICRUDSettings

def valid_schedule_config(v: str) -> str:
        def raise_exception():
            raise ValueError(
                'prsJsonConfigString должен быть вида '
                '{'
                '   "start": "<дата ISO8601>" | int, '
                '   "end": "<дата ISO8601>" | int | None, '
                '   "interval_type": "seconds | minutes | hours | days | None", '
                '   "interval_value": <int> | None'
                '} '
            )

        new_v = deepcopy(v)
        if not new_v:
            return {
                "start": t.ts_to_local_str(t.now_int()),
                "interval_type": "hours",
                "interval_value": 1
            }

        try:
            start = new_v.get("start", t.ts_to_local_str(t.now_int()))
            new_v["start"] = start
            interval_type = new_v.get("interval_type", "hours")
            interval_value = new_v.get("interval_value", 1)

            if interval_type not in ("seconds", "minutes", "hours", "days"):
                raise_exception()
            if not isinstance(interval_value, int):
                raise_exception()
            if interval_value < 1:
                raise_exception()

        except json.JSONDecodeError as ex:
            raise_exception()

        return new_v

class ScheduleCreateAttributes(svc.NodeAttributes):
    prsJsonConfigString: dict  = Field(
        {
            "start": t.ts_to_local_str(t.now_int()),
            "interval_type": "hours",
            "interval_value": 1
        }, title="Имя узла")
    
    validate_config = validator('prsJsonConfigString', allow_reuse=True)(valid_schedule_config)
    
class ScheduleCreate(svc.NodeCreate):
    attributes: ScheduleCreateAttributes = Field(ScheduleCreateAttributes(), title="Атрибуты узла")

    # validate_id = validator('parentId', 'dataStorageId', 'connectorId', allow_reuse=True)(svc.valid_uuid)

class ScheduleRead(svc.NodeRead):
    pass

class OneScheduleInReadResult(svc.OneNodeInReadResult):
    pass

class ScheduleReadResult(svc.NodeReadResult):
    data: List[OneScheduleInReadResult] = Field(title="Список расписаний.")
    pass

class ScheduleUpdate(svc.NodeUpdate):
    attributes: svc.NodeAttributes = Field({}, title="Атрибуты узла")

class SchedulesAPICRUD(svc.APICRUDSvc):
    """Сервис работы с расписаниями в иерархии.

    Формат ожидаемых сообщений

    """
    def __init__(self, settings: SchedulesAPICRUDSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def _create(self, payload: ScheduleCreate) -> dict:
        return await super()._create(payload=payload)

    async def _read(self, payload: ScheduleRead) -> dict:
        return await super()._read(payload=payload)

    async def _update(self, payload: ScheduleUpdate) -> dict:
        return await super()._update(payload=payload)

settings = SchedulesAPICRUDSettings()

app = SchedulesAPICRUD(settings=settings, title="`SchedulesAPICRUD` service")

router = APIRouter(prefix=f"{settings.api_version}/schedules")

@router.post("/", response_model=svc.NodeCreateResult, status_code=201)
async def create(payload: dict = None, error_handler: svc.ErrorHandler = Depends()):
    """
    Метод добавляет расписание в иерархию.

    **Запрос:**

        .. http:example::
            :request: ../../../../docs/source/samples/schedules/addScheduleIn.txt
            :response: ../../../../docs/source/samples/schedules/addScheduleOut.txt

        * **attributes** (dict) - словарь с параметрами для создания расписания.

          * **cn** (str) - имя расписания; Необязательный атрибут;
          * **description** (str) - описание экземпляра. Необязательный атрибут;
          * **prsJsonConfigString** (str) - Строка содержит, в случае необходимости,
            конфигурацию узла. Интерпретируется сервисом, управляющим сущностью,
            которой принадлежит экземпляр. Необязательный аттрибут
          * **prsActive** (bool) - Определяет, активен ли экземпляр. Необязательный атрибут;          

    **Ответ:**

        * **id** (uuid) - id созданного расписания
        * **detail** (str) - пояснения к ошибке

    """
    if payload is None:
        payload = {}
    
    try:
        s = json.dumps(payload)
        p = ScheduleCreate.model_validate_json(s)
    except Exception as ex:
        res = {"error": {"code": 422, "message": f"Несоответствие входных данных: {ex}"}}
        app._logger.exception(res)
        await error_handler.handle_error(res)

    res = await app._create(p)
    await error_handler.handle_error(res)
    return res

@router.get("/", response_model=svc.NodeReadResult | None, status_code=200, response_model_exclude_none=True)
async def read(q: str | None = None, payload: ScheduleRead | None = None):
    return await app.api_get_read(ScheduleRead, q, payload)

@router.put("/", status_code=202)
async def update(payload: ScheduleUpdate):
    await app._update(payload)

@router.delete("/", status_code=202)
async def delete(payload: ScheduleRead):
    await app.delete(payload)

app.include_router(router, tags=["schedules"])
