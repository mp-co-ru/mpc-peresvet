from pydantic import BaseModel, validator, Field, root_validator
from typing import List, Optional, Union, Any
import json
from ldap3 import LEVEL, DEREF_SEARCH
import validators
from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeCreateAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsDataStorageCreateAttrs(PrsModelNodeCreateAttrs):
    """
    Атрибуты сущности `dataStorage`.
    Используются при создании/изменении/получении хранилищ данных.
    """
    prsEntityTypeCode: int = Field(1, title='Код типа сущности',
        description=(
            '- 1 - Victoriametrics'
        )
    ) 

    @root_validator
    def check_vm_config(cls, values):
        type_code = values.get('prsEntityTypeCode')
        if type_code == 1:
            config = values.get('prsJsonConfigString')
            if config is not None:
                try:
                    js = json.loads(config)
                    put_url = js['putUrl']
                    get_url = js['getUrl']
                    if validators.url(put_url) and validators.url(get_url):
                       return values
                except:
                    pass

            raise ValueError((
                "Конфигурация (атрибут prsJsonConfigString) для Victoriametrics должна быть вида:\n"
                "{'putUrl': 'http://<server>:<port>/api/put', 'getUrl': 'http://<server>:<port>/api/v1/export'}"
            ))
        else:
            return values
    
class PrsDataStorageCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsDataStorageCreateAttrs = PrsDataStorageCreateAttrs(prsEntityTypeCode=0)

    @validator('parentId', check_fields=False, always=True)
    def parentId_must_be_none(cls, v):
        if v is not None:
            raise ValueError('parentId must be null for dataStorage')
        return v

class PrsDataStorageEntry(PrsModelNodeEntry):
    '''Базовый класс для всех хранилищ'''
    objectClass: str = 'prsDataStorage'
    payload_class = PrsDataStorageCreate
    default_parent_dn: str = "cn=dataStorages,{}".format(svc.config["LDAP_BASE_NODE"])

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)

        self.tags_cache = {}
        self._read_tags()
    
    def _read_tags(self):

        result, _, response, _ = svc.ldap.get_read_conn.search(
            search_base="cn=tags,{}".format(self.dn),
            search_filter='(cn=*)', search_scope=LEVEL, 
            dereference_aliases=DEREF_SEARCH, 
            attributes=['entryUUID', 'prsDataStore'])
        if not result:
            svc.logger.info("Нет привязанных тэгов к хранилищу '{}'".format(self.data.attributes.cn))
            return
        
        for item in response:
            attrs = dict(item['attributes'])
            self.tags_cache[attrs['entryUUID']] = attrs['prsDataStore']
        
        svc.logger.info("Тэги, привязанные к хранилищу `{}`, прочитаны.".format(self.data.attributes.cn))
        

    def connect(self): pass

    def set_data(self, data: List[Any]): pass

    def get_data(self, Any):  pass

    def _add_subnodes(self) -> None:
        data = PrsModelNodeCreate()
        data.parentId = self.id
        data.attributes = PrsModelNodeCreateAttrs(cn='tags')
        PrsModelNodeEntry(svc.ldap.get_write_conn(), data=data)

        data.attributes.cn = 'alerts'
        PrsModelNodeEntry(svc.ldap.get_write_conn(), data=data)
    
    def reg_tag(self, id: tag_id):
        