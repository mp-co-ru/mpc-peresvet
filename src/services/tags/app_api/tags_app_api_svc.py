"""
Модуль содержит классы, описывающие входные данные для команд CRUD для тегов
и класс сервиса ``tags_api_crud_svc``.
"""
import sys
from typing import Any, List, NamedTuple
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator, validator, BeforeValidator, ValidationError
import json
import random

from fastapi import APIRouter
from fastapi import WebSocket

sys.path.append(".")

from src.common import svc
from src.common.api_crud_svc import valid_uuid
from src.services.tags.app_api.tags_app_api_settings import TagsAppAPISettings
from src.common import times
import src.common.times as t

class DataPointItem(NamedTuple):
    y: float | dict | str | int | None = None
    x: int | str | None = None
    q: int | None = None

def x_must_be_int(v):
    match len(v):
        case 0:
            return DataPointItem(None, t.ts(None), None)
        case 1:
            return DataPointItem(v[0], t.ts(None), None)
        case 2:
            return DataPointItem(v[0], t.ts(v[1]), None)
        case 3:
            return DataPointItem(v[0], t.ts(v[1]), v[2])

    return v

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
        #default_factory=t.now_int,
        None,
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
        # если finish в виде строки, то строка должна быть в формате ISO8601
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
        # если finish в виде строки, то строка должна быть в формате ISO8601
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
        self.cache_data = {}

    def _set_incoming_commands(self) -> dict:
        return {
            "client.getData": self.data_get
        }

    async def on_startup(self) -> None:
        await super().on_startup()

        ids = [
            "2e377cf0-c183-103d-85bd-75a6e9de364f",
            "2e3e287a-c183-103d-85c0-75a6e9de364f",
            "2e46700c-c183-103d-85c5-75a6e9de364f",
            "2e4f1de2-c183-103d-85ca-75a6e9de364f",
            "2e5587a4-c183-103d-85cf-75a6e9de364f",
            "2e5c0ac0-c183-103d-85d4-75a6e9de364f",
            "2e622842-c183-103d-85d8-75a6e9de364f",
            "2e67fdda-c183-103d-85dc-75a6e9de364f",
            "2e6e359c-c183-103d-85e1-75a6e9de364f",
            "2e751da8-c183-103d-85e6-75a6e9de364f",
            "2e7b39c2-c183-103d-85eb-75a6e9de364f",
            "2e81bb8a-c183-103d-85f0-75a6e9de364f",
            "2e891ae2-c183-103d-85f5-75a6e9de364f",
            "2e9196ae-c183-103d-85fa-75a6e9de364f",
            "2e9828e8-c183-103d-85fd-75a6e9de364f",
            "2ea0162a-c183-103d-8602-75a6e9de364f",
            "2ea6ff44-c183-103d-8607-75a6e9de364f",
            "2eadc1e4-c183-103d-860c-75a6e9de364f",
            "2eb449e2-c183-103d-8611-75a6e9de364f",
            "2ebaf166-c183-103d-8616-75a6e9de364f",
            "2ec12946-c183-103d-861b-75a6e9de364f",
            "2ec7c580-c183-103d-8620-75a6e9de364f",
            "2ecef274-c183-103d-8625-75a6e9de364f",
            "2ed6d94e-c183-103d-862a-75a6e9de364f",
            "2ede0e76-c183-103d-862d-75a6e9de364f",
            "2ee53070-c183-103d-8632-75a6e9de364f",
            "2eebeb22-c183-103d-8637-75a6e9de364f",
            "2ef1cb00-c183-103d-863c-75a6e9de364f",
            "2ef7fbba-c183-103d-8640-75a6e9de364f",
            "2efdd5a8-c183-103d-8644-75a6e9de364f",
            "2f048128-c183-103d-8649-75a6e9de364f",
            "2f0a899c-c183-103d-864e-75a6e9de364f",
            "2f10901c-c183-103d-8653-75a6e9de364f",
            "2f16e7c8-c183-103d-8657-75a6e9de364f",
            "2f1d2cd2-c183-103d-865b-75a6e9de364f",
            "2f2a66ae-c183-103d-8662-75a6e9de364f",
            "2f310130-c183-103d-8665-75a6e9de364f",
            "2f38e44a-c183-103d-866a-75a6e9de364f",
            "2f42fd86-c183-103d-866f-75a6e9de364f",
            "2f4d209a-c183-103d-8674-75a6e9de364f",
            "2f53f906-c183-103d-8679-75a6e9de364f",
            "2f5ac83a-c183-103d-867d-75a6e9de364f",
            "2f61d6fc-c183-103d-8681-75a6e9de364f",
            "2f69512a-c183-103d-8686-75a6e9de364f",
            "2f73919e-c183-103d-868b-75a6e9de364f",
            "2f7e7e10-c183-103d-868f-75a6e9de364f",
            "2f89c4aa-c183-103d-8693-75a6e9de364f",
            "2f919dce-c183-103d-8698-75a6e9de364f",
            "2f98b514-c183-103d-869d-75a6e9de364f",
            "2f9f1198-c183-103d-86a2-75a6e9de364f",
            "2fa728ba-c183-103d-86a7-75a6e9de364f",
            "2fb0147a-c183-103d-86ab-75a6e9de364f",
            "2fb881d2-c183-103d-86af-75a6e9de364f",
            "2fc07cde-c183-103d-86b4-75a6e9de364f",
            "2fc8fa76-c183-103d-86b9-75a6e9de364f",
            "2fd21908-c183-103d-86be-75a6e9de364f",
            "2fd9f1e6-c183-103d-86c3-75a6e9de364f",
            "2fe0fc20-c183-103d-86c6-75a6e9de364f",
            "2fe7e3b4-c183-103d-86cb-75a6e9de364f",
            "2fef2598-c183-103d-86d0-75a6e9de364f",
            "2ff61b50-c183-103d-86d5-75a6e9de364f",
            "2ffcf9f2-c183-103d-86da-75a6e9de364f",
            "3002f046-c183-103d-86de-75a6e9de364f",
            "300accda-c183-103d-86e2-75a6e9de364f",
            "3012b21a-c183-103d-86e7-75a6e9de364f",
            "301a3f9e-c183-103d-86ec-75a6e9de364f",
            "30210ad6-c183-103d-86f1-75a6e9de364f",
            "30282e74-c183-103d-86f6-75a6e9de364f",
            "302f0910-c183-103d-86fa-75a6e9de364f",
            "3036dfe6-c183-103d-86fe-75a6e9de364f",
            "303e62de-c183-103d-8703-75a6e9de364f",
            "3046a6c4-c183-103d-8708-75a6e9de364f",
            "304eaef0-c183-103d-870d-75a6e9de364f",
            "3055cd0c-c183-103d-8712-75a6e9de364f",
            "305d0dec-c183-103d-8715-75a6e9de364f",
            "30651de8-c183-103d-871a-75a6e9de364f",
            "306cb602-c183-103d-871f-75a6e9de364f",
            "3073cb04-c183-103d-8724-75a6e9de364f",
            "307a1b1c-c183-103d-8729-75a6e9de364f",
            "30806d5a-c183-103d-872e-75a6e9de364f",
            "3086ba5c-c183-103d-8733-75a6e9de364f",
            "308ca28c-c183-103d-8736-75a6e9de364f",
            "3093b7de-c183-103d-873b-75a6e9de364f",
            "309b2564-c183-103d-8740-75a6e9de364f",
            "30a23d86-c183-103d-8745-75a6e9de364f",
            "30a8f158-c183-103d-8749-75a6e9de364f",
            "30b059c0-c183-103d-874d-75a6e9de364f",
            "30b85f30-c183-103d-8752-75a6e9de364f",
            "30c018c4-c183-103d-8757-75a6e9de364f",
            "30c66b70-c183-103d-875c-75a6e9de364f",
            "30cc6278-c183-103d-8761-75a6e9de364f",
            "30d23cd4-c183-103d-8766-75a6e9de364f",
            "30d7fbd8-c183-103d-8769-75a6e9de364f",
            "30dea780-c183-103d-876e-75a6e9de364f",
            "30e52e66-c183-103d-8773-75a6e9de364f",
            "30ecd12a-c183-103d-8778-75a6e9de364f",
            "30f3f950-c183-103d-877d-75a6e9de364f",
            "30faf7d2-c183-103d-8781-75a6e9de364f",
            "310357c4-c183-103d-8786-75a6e9de364f",
            "310a5506-c183-103d-878a-75a6e9de364f"
        ]
        for id in ids:
            self.cache_data[id] = []
            for _ in range(24):
                self.cache_data[id].append([random.randint(-100, 100), times.now_int(), None])
        self._logger.info("Кэш данных сформирован.")

    async def data_get(self, payload: DataGet) -> dict:
        if isinstance(payload, dict):
            payload = payload["data"]
            payload = DataGet(**payload)

        res = {
            "data": []
        }

        if not payload.start:
            for tag_id in payload.tagId:
                res["data"].append({
                    "tagId": tag_id,
                    "data": [self.cache_data[tag_id][0]]
                })
        else:
            for tag_id in payload.tagId:
                res["data"].append({
                    "tagId": tag_id,
                    "data": self.cache_data[tag_id]
                })

        return res

        '''
        body = {
            "action": "tags.getData",
            "data": payload.model_dump()
        }
        result = await self._post_message(
            mes=body, reply=True,
        )
        '''
        '''
        if len(payload.tagId) > 10:
            splitted_tags = np.array_split(payload.tagId, 4)
        else:
            splitted_tags = [payload.tagId]
        body = {
            "action": "tags.downloadData",
            "data": payload.model_dump()
        }
        tasks = []
        for splitted in splitted_tags:
            body["data"]["tagId"] = list(splitted)
            tasks.append(
                asyncio.create_task(
                    self._post_message(
                        mes=body, reply=True, routing_key="ac258e2a-b8f7-103d-9a07-6fcde61b9a51"
                    )
                )
            )

        done, _ = await asyncio.wait(
            tasks, return_when=asyncio.ALL_COMPLETED
        )

        result = {
            "data": []
        }
        for future in done:
            res = future.result()

            result["data"].extend(res["data"])


        """
        body = {
            "action": "tags.downloadData",
            "data": payload.model_dump()
        }
        result = await self._post_message(
            mes=body, reply=True, routing_key="ac258e2a-b8f7-103d-9a07-6fcde61b9a51"
        )
        """
        '''

        if payload.format:
            final_res = {
                "data": []
            }

            for tag_item in result["data"]:
                new_tag_item = {
                    "tagId": tag_item["tagId"],
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

        return result

    async def data_set(self, payload: AllData) -> None:
        body = {
            "action": "tags.setData",
            "data": payload.model_dump()
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
