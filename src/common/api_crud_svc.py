"""
Модуль содержит классы, описывающие форматы входных данных для команд,
а также класс APICRUDSvc - базовый класс для всех сервисов
<сущность>_api_crud.
"""
import json
from typing import Union
from uuid import UUID
from pydantic import BaseModel, Field, validator, ConfigDict
from fastapi import HTTPException
from src.common.base_svc import BaseSvc
from src.common.api_crud_settings import APICRUDSettings

def valid_uuid(id: str | list[str]) -> str | list[str]:
    """Валидатор идентификаторов.
    Идентификатор должен быть в виде GUID.
    """
    if id is not None:
        try:
            if isinstance(id, str):
                UUID(id)
            else:
                for item in id:
                    UUID(item)
        except ValueError as ex:
            raise ValueError('id должен быть в виде GUID') from ex
    return id


# класс с методами обработки ошибок в выоде для пользователя
class ErrorHandler:
    async def handle_error(self,res):
        if res is not None:
            if ("error" in res) and ("code" in res["error"]) and ("message" in res["error"]):
                raise HTTPException(status_code=res["error"]["code"], detail=res["error"]["message"])
            elif ("error" in res):
                raise HTTPException(status_code=400, detail=res["error"])


class NodeAttributes(BaseModel):
    """Атрибуты для создания базового узла.
    """
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    cn: str = Field(None, title="Имя узла")
    description: str | None = Field(None, title="Описание",
        description="Описание экземпляра.")
    prsJsonConfigString: str | None = Field(None, title="Конфигурация экземпляра.",
        description=(
            "Строка содержит, в случае необходимости, конфигурацию узла. "
            "Интерпретируется сервисом, управляющим сущностью, которой "
            "принадлежит экземпляр."
        ))
    prsActive: bool = Field(True, title="Флаг активности.",
        description=(
            "Определяет, активен ли экземпляр. Применяется, к примеру, "
            "для временного 'выключения' экземпляра на время, пока он ещё "
            "недонастроен."
        )
    )

    prsDefault: bool | None = Field(None, title="Сущность по умолчанию.",
        description=(
            "Если = ``True``\, то данный экземпляр считается узлом по умолчанию "
            "в списке равноправных узлов данного уровня иерархии."
        )
    )
    prsEntityTypeCode: int | None = Field(None, title="Тип узла.",
        description=(
            "Атрибут используется для определения типа. К примеру, "
            "хранилища данных могут быть разных типов."
        )
    )
    prsIndex: int | None = Field(None, title="Индекс узла.",
        description=(
            "Если у узлов одного уровня иерархии проставлены индексы, то "
            "перед отдачей клиенту списка экземпляров они сортируются "
            "в соответствии с их индексами."
        )
    )

class NodeCreate(BaseModel):
    """Базовый класс для команды создания экземпляра сущности.
    """
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    parentId: str | None = Field(None, title="Id родительского узла",
        description=(
            "Идентификатор родительского узла. "
            "Если используется в команде создания узла, то в случае "
            "отсутствия экзмепляр создаётся в базовом для данной "
            "сущности узле. "
            "При использовании в команде изменения узла трактуется как новый "
            "родительский узел."
        ))
    attributes: NodeAttributes = Field({}, title="Атрибуты узла")

    validate_id = validator('parentId', allow_reuse=True)(valid_uuid)

class NodeDelete(BaseModel):
    """Базовый класс, описывающий параметры
    команды для удаления узла.
    """
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    id: str | list[str] = Field(title="Идентификатор(ы) узла.",
        description=(
            "Идентификатор(ы) удаляемого(изменяемого) узла "
            "должен быть в виде uuid."
        )
    )

    validate_id = validator('id', allow_reuse=True)(valid_uuid)

    @validator('id')
    @classmethod
    def make_id_as_array(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v

class NodeUpdate(NodeCreate):
    """Базовый класс для изменения узла
    """
    id: str = Field(title="Идентификатор изменяемого узла.",
                    description="Должен быть в формате GUID.")

    validate_id = validator('parentId', 'id', allow_reuse=True)(valid_uuid)

class NodeRead(BaseModel):
    """Базовый класс, описывающий параметры для команды
    поиска/чтения узлов.
    """
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    id: str | list[str] = Field(
        None,
        title="Идентификатор(ы) узлов.",
        description=(
            "Если уазан(ы), то возвращаются данные по указанному(ым) "
            "узлам. В этом случае ключи `base`, `scope`, `filter` "
            "не принимаются во внимание."
        )
    )
    base: str | None = Field(
        None,
        title="Базовый узел для поиска.",
        description="Если не указан, то поиск ведётся от главного узла иерархии."
    )
    deref: bool = Field(
        True,
        title="Флаг разыменования ссылок.",
        description="По умолчанию = true."
    )
    scope: int = Field(
        1,
        title="Масштаб поиска.",
        description=(
            "0 - получение данных по указанному в ключе ``base`` узлу;"
            "1 - поиск среди непосредственных потомков указанного в ``base`` узла;"
            "2 - поиск по всему дереву, начиная с указанного в ``base`` узла."
        )
    )
    filter: dict | None = Field(
         None,
         title=(
            "Словарь из атрибутов и их значений, из "
            "которых формируется фильтр для поиска."
         ),
         description=(
            "Значения одного атрибута объединяются логической операцией ``ИЛИ``\, "
            "затем значения для разных атрибутов объединяются операцией ``И``\."
         )
    )
    attributes: list[str] = Field(
        ['*'],
        title="Список атрибутов.",
        description=(
            "Список атрибутов, значения которых необходимо вернуть "
            "в ответе. По умолчанию - ['\*'], то есть все атрибуты "
            "(кроме системных)."
        )
    )

    validate_id = validator('id', 'base', allow_reuse=True)(valid_uuid)

class NodeCreateResult(BaseModel):
    """Результат выполнения команды создания узла.
    """
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    id: Union[str, None]


class OneNodeInReadResult(BaseModel):
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(title="Id узла.")
    attributes: dict = Field(title="Атрибуты узла")

class NodeReadResult(BaseModel):
    # https://giters.com/pydantic/pydantic/issues/6322
    model_config = ConfigDict(protected_namespaces=())

    data: list[OneNodeInReadResult] = Field(title="Список узлов")

class APICRUDSvc(BaseSvc):
    _outgoing_commands = {
        "create": "create",
        "read": "read",
        "update": "update",
        "delete": "delete"
    }

    def __init__(self, settings: APICRUDSettings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)

        self.api_version = settings.api_version

    async def create(self, payload: NodeCreate) -> dict:
        body = {
            "action": self._outgoing_commands["create"],
            "data": payload.model_dump()
        }

        return await self._post_message(mes=body, reply=True)

    async def read(self, payload: NodeRead) -> dict:
        body = {
            "action": self._outgoing_commands["read"],
            "data": payload.model_dump()
        }

        return await self._post_message(mes=body, reply=True)


    async def update(self, payload: NodeUpdate) -> dict:
        body = {
            "action": self._outgoing_commands["update"],
            "data": payload.model_dump()
        }

        return await self._post_message(mes=body, reply=True)

    async def delete(self, payload: NodeDelete) -> dict:
        """Удаление узлов в иерархии.
        """
        body = {
            "action": self._outgoing_commands["delete"],
            "data": payload.model_dump()
        }

        return await self._post_message(mes=body, reply=True)

    async def api_get_read(self, request_model: NodeRead, q: str | None, payload: NodeRead | None):
        if q is None and payload is None:
            q = "{}"
        if q:
            try:
               #q_js = json.loads(q)
                p = request_model.model_validate_json(q)
            except Exception as ex:
                err = f"Ошибка чтения: {ex}"
                self._logger.exception(err)
                return {"error": err}
        elif payload:
            p = payload


        return await self.read(p)
