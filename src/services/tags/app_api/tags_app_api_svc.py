"""
Модуль содержит классы, описывающие входные данные для команд CRUD для тегов
и класс сервиса ``tags_api_crud_svc``.
"""
import sys
from typing import Any, List, NamedTuple
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator, validator, BeforeValidator, ValidationError
import json

from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import HTTPException, WebSocketException

sys.path.append(".")

from src.common import svc
from src.common.api_crud_svc import valid_uuid
from src.services.tags.app_api.tags_app_api_settings import TagsAppAPISettings
import src.common.times as t

class DataPointItem(NamedTuple):
    y: float | dict | str | int | None = None
    x: int | str | None = None
    q: int | None = None

def x_must_be_int(v):
    return DataPointItem(v.y, t.ts(v.x), v.q)

class TagData(BaseModel):
    tagId: str = Field(
        title="id тега"
    )
    data: List[Annotated[DataPointItem, BeforeValidator(x_must_be_int)]]

    validate_id = validator('tagId', allow_reuse=True)(valid_uuid)

class AllData(BaseModel):
    data: List[TagData] = Field(
        title="Данные"
    )

class DataGet(BaseModel):
    tagId: str | list[str] = Field(
        title="Id или список id тегов"
    )
    start: int | str = Field(
        None,
        title="Метка времени начала периода."
    )
    finish: int | str = Field(
        default_factory=t.now_int,
        title="Метка времени окончания периода."
    )
    maxCount: int = Field(
        None,
        title="Максимальное количество точек в ответе."
    )
    format: bool = Field(
        False,
        title="Флаг форматирования меток времени в строку формата ISO8601"
    )
    actual: bool = Field(
        False,
        title="Флаг возврата только реально записанных данных."
    )
    value: Any = Field(
        None,
        title="Фильтр по значению"
    )
    count: int = Field(
        None,
        title="Количество запрашиваемых точек."
    )
    timeStep: int = Field(
        None,
        title="Шаг между соседними значениями."
    )

    @validator('tagId')
    @classmethod
    def tagId_list(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [v]
        else:
            return v

    @validator('finish')
    @classmethod
    def finish_in_iso_format(cls, v: Any) -> int:
        # если finish в виде строки, то строка должна быть в формате ISO9601
        try:
            return t.ts(v)
        except ValueError as ex:
            raise ValueError(
                (
                    "Метка времени должна быть строкой в формате ISO8601, "
                    "целым числом или отсутствовать."
                )
            )

    @validator('start')
    @classmethod
    def start_in_iso_format(cls, v: Any) -> int:
        if v is None:
            return
        # если finish в виде строки, то строка должна быть в формате ISO9601
        try:
            return t.ts(v)
        except ValueError as ex:
            raise ValueError(
                (
                    "Метка времени должна быть строкой в формате ISO8601, "
                    "целым числом или отсутствовать."
                )
            )

    validate_id = validator('tagId', allow_reuse=True)(valid_uuid)

class TagsAppAPI(svc.Svc):
    """Сервис работы с тегами в иерархии.

    Подписывается на очередь ``tags_api_crud`` обменника ``tags_api_crud``,
    в которую публикует сообщения сервис ``tags_api_crud`` (все имена
    указываются в переменных окружения).

    Формат ожидаемых сообщений

    """

    _outgoing_commands = {}

    def __init__(self, settings: TagsAppAPISettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

    async def data_get(self, payload: DataGet) -> dict:

        body = {
            "action": "tags.get_data",
            "data": payload.model_dump()
        }

        res = await self._post_message(mes=body, reply=True)

        final_res = {
            "data": []
        }
        if payload["format"]:
            for tag_item in res["data"]:
                new_tag_item = {
                    "tagId": new_tag_item["tagId"],
                    "data": []
                }
                for data_item in tag_item["data"]:
                    new_tag_item["data"].append((
                        data_item[0],
                        t.int_to_local_timestamp(data_item[1]),
                        data_item[2]
                    ))
                final_res["data"].append(new_tag_item)

        return final_res

    async def data_set(self, payload: AllData) -> None:
        body = {
            "action": "tags.set_data",
            "data": {
                "data": payload
            }
        }

        return await self._post_message(mes=body, reply=False)

settings = TagsAppAPISettings()

app = TagsAppAPI(settings=settings, title="`TagsAppAPI` service")

router = APIRouter()

@router.get("/", response_model=dict, status_code=200)
async def data_get(payload: DataGet):
    res = await app.data_get(payload)
    return res

@router.post("/", status_code=200)
async def data_set(payload: AllData):
    return await app.data_set(payload)

@app.websocket(f"{settings.api_version}/ws/data")
async def websocket_endpoint(websocket: WebSocket):

    try:
        await websocket.accept()
        app._logger.debug(f"Установлена ws-связь.")

        while True:
            try:
                received_data = await websocket.receive_json()
                action = received_data.get("action")
                if not action:
                    raise ValueError("Не указано действие в команде.")
                data = received_data.get("data")
                if not data:
                    raise ValueError("Не указаны данные команды.")

                match action:
                    case "get":
                        res = await app.data_get(DataGet(**data))
                    case "set":
                        await app.data_set(AllData(**data))
                        res = {
                            "error": {"id": 0}
                        }
                await websocket.send_json(res)

            except TypeError as ex:
                app._logger.error(f"Неверный формат данных: {ex}")
            except ValidationError as ex:
                app._logger.error(f"Неверные данные сообщения: {ex}")
            except json.JSONDecodeError as ex:
                app._logger.error(f"Сообщение должно быть в виде json: {ex}")
            except ValueError as ex:
                app._logger.error(ex)

    except Exception as ex:
        app._logger.error(f"Разрыв ws-связи: {ex}")

app.include_router(router, prefix=f"{settings.api_version}/data", tags=["data"])