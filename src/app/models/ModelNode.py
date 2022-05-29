from uuid import uuid4, UUID

from fastapi import HTTPException
from ldap3 import ObjectDef, Reader, Writer, SUBTREE, BASE, DEREF_NEVER, ALL_ATTRIBUTES, MODIFY_REPLACE
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union, Dict
import json

import app.main as main
from app.svc.Services import Services as svc

class PrsModelNodeCreateAttrs(BaseModel):
    """Pydantic BaseModel for prsBaseModel attributes
    """
    cn: Union[str, List[str]] = Field(None, title="Имя узла",
        description="Имя вновь создаваемого узла. В случае, если отсутствует, имя узла будет совпадать с его `id`")
    description: Union[str, List[str]] = Field(None, title="Описание узла")
    prsSystemNode: Optional[bool] = Field(False, title="Флаг системного узла",
        description=(
            "Если равен `True`, то узел иерархии является системным, не предназначенным для показа пользователю. "
            "К примеру, можно создать расчётные тэги, не предназначенные для просмотра обычным пользователем. "
            "Включив этот флаг у таких тэгов, мы исключим появление тэгов в списке, допустим, тренда. "
    ))
    prsEntityTypeCode: int = Field(None, title='Код типа сущности',
        description=(
            'По разному интерпретируется для разных сущностей. Например, для тэгов: 1 - обычный тэг, 2 - вычислимый. '
            'Подробней - в документации на каждую сущность.'
        )
    )
    prsJsonConfigString: Union[Dict, str] = Field(None, title="Строка с json-конфигурацией.",
        description=(
            'Атрибут может содержать строку с json-конфигурацией для сущности. Подробней - в документации на каждую сущность.'
        ))
    prsIndex: int = Field(None, title='Индекс сущности в списке',
        description=(
            'Индекс сущности служит для сортировки списков. Допустим, если в иерархии содержатся узлы с индексами, '
            'то при возврате списка таких узлов клиенту они будут сортироваться согласно своим индексам.'
        )
    )
    prsDefault: bool = Field(None, title='Флаг сущности по умолчанию',
        description=(
            'Пример применения флага: допустим, имеем в списке несколько хранилищ данных. У одного из них флаг '
            '`Default = True`, тогда при создании тэга, если не указано явно, в какое хранилище записывать его данные, '
            'по умолчанию будет использоваться указанное.'
        )
    )
    prsActive: bool = Field(True, title='Флаг активности',
        description=(
            'Флаг активности сущности. Например, в тэг с флагом `prsActive = False` не записываются данные, не производятся его расчёты и т.д. '
            'Подробней - в документации на каждую сущность.'
        )
    )
    prsApp: Union[str, List[str]] = Field(None, title='Список приложений',
        description=(
            'Атрибут может использоваться в случае, если к одной иерархии обращаются несколько разных приложений. '
            'В этом случае, при запросе на получение сущностей, приложение указывает свое имя и получает список предназначенных ему сущностей.'
        )
    )
    @classmethod
    @validator('cn', 'description', 'prsApp')
    def empty_list_is_none(cls, v):
        if isinstance(v, list) and len(v)==0:
            return None
        return v

class PrsModelNodeCreate(BaseModel):
    """Class for http requests validation"""
    parentId: str = None # uuid of parent node
    attributes: PrsModelNodeCreateAttrs = PrsModelNodeCreateAttrs()

    @classmethod
    @validator('parentId', check_fields=False)
    def parentId_must_be_uuid_or_none(cls, v):
        if v is not None:
            try:
                UUID(v)
            except:
                raise ValueError('parentId must be uuid')
        return v

class PrsResponseCreate(BaseModel):
    """Response for POST-request for entity creation"""
    id: str

class PrsModelNodeEntry:
    """
    Базовый класс для представления узла иерархии.

    Каждый класс-наследник должен переопределить:

    objectClass (str) - имя класса в схеме ldap
    default_parent_dn (str) - имя родительского узла в иерархии по умолчанию
    payload_class (class) - класс, используемых в запросах создания/получения данных

    _add_subnodes - добавление дочерних узлов
    _add_fields_to_get_response - добавление к стандартному ответу, отдаваемому клиенту при его запросе get дополнительных атрибутов.
    Например, тэг должен в parentId отдать id родительского объекта или None, а также добавить к ответу атрибуты connectorId и dataStorageId
    """
    objectClass: str = 'prsModelNode'
    default_parent_dn: str = svc.config["LDAP_BASE_NODE"]
    payload_class = PrsModelNodeCreate

    def _add_subnodes(self) -> None:
        pass

    def __init__(self, data: PrsModelNodeCreate = None, id: str = None):
        # сохраняем коннект на время создания/чтения узла, в конце конструктора - освобождаем
        # делаем так, чтобы не плодить активных коннектов
        # в случае, когда необходимо будет реагировать на
        if id is None:
            conn = svc.ldap.get_write_conn()
        else:
            conn = svc.ldap.get_read_conn()

        ldap_cls_def = ObjectDef(self.__class__.objectClass, conn)
        ldap_cls_def += ['entryUUID']

        if id is None:
            if data.parentId is None:
                parent_dn = self.__class__.default_parent_dn
            else:
                parent_dn = main.app.get_node_dn_by_id(data.parentId)

            reader = Reader(conn, ldap_cls_def, parent_dn)
            reader.search()
            writer = Writer.from_cursor(reader)
            if data.attributes.cn is None:
                cn = str(uuid4())
            elif isinstance(data.attributes.cn, str):
                cn = data.attributes.cn
            else:
                cn = data.attributes.cn[0]

            entry = writer.new(f'cn={cn},{parent_dn}')
            for key, value in data.attributes.__dict__.items():
                if value is not None:
                    if isinstance(value, dict):
                        value = json.dumps(value)
                    entry[key] = value
            entry.entry_commit_changes()

            # прочитаем ID нового узла
            _, _, response, _ = conn.search(search_base=entry.entry_dn,
                search_filter='(cn=*)', search_scope=BASE, dereference_aliases=DEREF_NEVER, attributes='entryUUID')
            attrs = dict(response[0]['attributes'])
            self.id = attrs['entryUUID']

            self.data = data.copy(deep=True)
            if data.attributes.cn is None:
                self.data.attributes.cn = self.id
                entry.entry_rename(f"cn={self.id}")
                entry.entry_commit_changes()

            self.dn = entry.entry_dn

            self._add_subnodes()
        else:
            try:
                UUID(id)
            except:
                raise HTTPException(status_code=422, detail=f"Некорректный формат id: {id}.")

            self.data = self.__class__.payload_class()
            status, _, response, _ = conn.search(search_base=svc.config["LDAP_BASE_NODE"],
                search_filter=f'(entryUUID={id})', search_scope=SUBTREE, dereference_aliases=DEREF_NEVER, attributes=[ALL_ATTRIBUTES])
            if not status:
                raise HTTPException(status_code=404, detail=f"Сущность с id = {id} отсутствует.")
            attrs = dict(response[0]['attributes'])
            self.id = id

            attrs.pop("objectClass")

            for key, value in attrs.items():
                if ldap_cls_def[key].oid_info.syntax == '1.3.6.1.4.1.1466.115.121.1.36':
                    value = float(value)
                self.data.attributes.__setattr__(key, value)

            self.dn = response[0]['dn']
            self._load_subnodes()

    def _load_subnodes(self):
        """
        Метод, переопределяемый в классах-наследниках для дочитывания дополнительных узлов.
        """
        pass

    def get_id(self) -> str:
        return self.id

    def modify(self, attrs: Dict):
        """ perform the Modify operation
        :param attrs: атрибуты для изменения. Формат: {"cn": ["new_val"], "prsIndex": 1}
        :type attrs: dict
        """
        conn = svc.ldap.get_write_conn()
        new_attrs = {key: [(MODIFY_REPLACE, value)] for key, value in attrs.items()}

        conn.modify(self.dn, new_attrs)
