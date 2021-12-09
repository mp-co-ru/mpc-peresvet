from ldap3 import Connection, ObjectDef, Reader, Writer, SUBTREE, BASE, DEREF_NEVER, ALL_ATTRIBUTES, Entry
from uuid import uuid4, UUID
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union
import json

from app.svc.Services import Services as svc
import app.main as main

class PrsModelNodeAttrs(BaseModel):
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
    prsJsonConfigString: str = Field(None, title="Строка с json-конфигурацией.",
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
    
    @validator('cn', 'description', 'prsApp')
    def empty_list_is_none(cls, v):
        if isinstance(v, list) and len(v)==0:
            return None
        return v

    '''
    class Item(BaseModel):
        name: str
        description: Optional[str] = Field(
            None, title="The description of the item", max_length=300
        )
        price: float = Field(..., gt=0, description="The price must be greater than zero")
        tax: Optional[float] = None


    @app.put("/items/{item_id}")
    async def update_item(item_id: int, item: Item = Body(..., embed=True)):
        results = {"item_id": item_id, "item": item}
        return results
    '''

class PrsModelNodeCreate(BaseModel):
    """Class for http requests validation"""
    parentId: str = None # uuid of parent node
    attributes: PrsModelNodeAttrs = PrsModelNodeAttrs()
    
    @validator('parentId')
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
    objectClass: str = 'prsModelNode'
    default_parent_dn: str = svc.config["LDAP_BASE_NODE"]
    payload_class = PrsModelNodeCreate

    def _add_subnodes(self) -> None:
        pass
    
    def __init__(self, conn: Connection, data: PrsModelNodeCreate = None, id: str = None):
        self.conn = conn
        ldap_cls_def = ObjectDef(self.__class__.objectClass, self.conn)
        ldap_cls_def += ['entryUUID']
            
        if id is None:
            if data.parentId is None:
                parent_dn = self.__class__.default_parent_dn
            else:
                parent_dn = main.app.get_node_dn_by_id(data.parentId)
                
            reader = Reader(self.conn, ldap_cls_def, parent_dn)
            reader.search()
            writer = Writer.from_cursor(reader)
            if data.attributes.cn is None:
                cn = str(uuid4())
            elif isinstance(data.attributes.cn, str):
                cn = data.attributes.cn
            else: 
                cn = data.attributes.cn[0]

            entry = writer.new('cn={},{}'.format(cn, parent_dn))
            for key, value in data.attributes.__dict__.items():
                if value is not None:
                    entry[key] = value
            entry.entry_commit_changes()

            # прочитаем ID нового узла
            _, _, response, _ = self.conn.search(search_base=entry.entry_dn,
                search_filter='(cn=*)', search_scope=BASE, dereference_aliases=DEREF_NEVER, attributes='entryUUID')
            attrs = dict(response[0]['attributes'])
            self.id = attrs['entryUUID']

            self.data = data.copy(deep=True)
            if data.attributes.cn is None:
                self.data.attributes.cn = self.id
                entry.entry_rename("cn={}".format(self.id))
                entry.entry_commit_changes()
            
            self.dn = entry.entry_dn
            
            self._add_subnodes()
        else: 
            self.data = self.__class__.payload_class()
            _, _, response, _ = self.conn.search(search_base=svc.config["LDAP_BASE_NODE"],
                search_filter='(entryUUID={})'.format(id), search_scope=SUBTREE, dereference_aliases=DEREF_NEVER, attributes=[ALL_ATTRIBUTES])
            attrs = dict(response[0]['attributes'])
            self.id = id

            attrs.pop("objectClass")
            for key, value in attrs.items():
                self.data.attributes.__setattr__(key, value)
            
            self.dn = response[0]['dn']

    def get_id(self) -> str:        
        return self.id

    def _add_fields_to_get_response(self, data): 
        '''
        Метод вызывается из метода form_get_response для того, чтобы каждый класс-наследник добавлял к формируемому ответу свои поля.
        '''
        return data

    def form_get_response(self):
        '''
        Метод возвращает класс для ответов по запросам GET.
        Не храним этот класс всегда, чтобы не дублировать данные.
        Используем обычный запрос к ldap, а не существующий уже self.entry потому, что self.entry всегда возвращает атрибуты в виде массивов.
        '''
        data = self.data.copy(deep=True)
        data = self._add_fields_to_get_response(data)
        return data
    