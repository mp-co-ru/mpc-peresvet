from pydantic import validator, Field, root_validator
from typing import List, Union, Dict
import json
from ldap3 import LEVEL, DEREF_SEARCH, ALL_ATTRIBUTES
import validators
from app.svc.Services import Services as svc
import app.models.ModelNode as m_mn
import app.models.Tag as m_tag
from app.const import *

class PrsDataStorageCreateAttrs(m_mn.PrsModelNodeCreateAttrs):
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
    
class PrsDataStorageCreate(m_mn.PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsDataStorageCreateAttrs = PrsDataStorageCreateAttrs(prsEntityTypeCode=CN_DS_POSTGRESQL)

    @validator('parentId', check_fields=False, always=True)
    def parentId_must_be_none(cls, v):
        if v is not None:
            raise ValueError('parentId must be null for dataStorage')
        return v

class PrsDataStorageEntry(m_mn.PrsModelNodeEntry):
    '''Базовый класс для всех хранилищ'''
    objectClass: str = 'prsDataStorage'
    payload_class = PrsDataStorageCreate
    default_parent_dn: str = svc.config["LDAP_DATASTORAGES_NODE"]

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)
        
        self.tags_node = "cn=tags,{}".format(self.dn)
        self._read_tags()        
    
    def _format_data_store(self, attrs: Dict) -> Union[None, Dict]:
        res = attrs.get['prsStore']
        if res is not None:
            try:
                res = json.loads(attrs['prsStore'])
            except:
                pass

        return res

    def _read_tags(self):

        result, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=self.tags_node,
            search_filter='(cn=*)', search_scope=LEVEL, 
            dereference_aliases=DEREF_SEARCH, 
            attributes=[ALL_ATTRIBUTES, 'entryUUID'])
        if not result:
            svc.logger.info("Нет привязанных тэгов к хранилищу '{}'".format(self.data.attributes.cn))
            return
        
        tags = []
        for item in response:
            tags.append(str(item['attributes']['entryUUID']))
            self.reg_tags(tags)            
        
        svc.logger.info("Тэги, привязанные к хранилищу `{}`, прочитаны.".format(self.data.attributes.cn))        

    async def connect(self): pass

    async def set_data(self, data): pass

    async def get_data(self, Any):  pass

    def _add_subnodes(self) -> None:
        data = m_mn.PrsModelNodeCreate()
        data.parentId = self.id
        data.attributes = m_mn.PrsModelNodeCreateAttrs(cn='tags')
        m_mn.PrsModelNodeEntry(data=data)

        data.attributes.cn = 'alerts'
        m_mn.PrsModelNodeEntry(data=data)
    
    def reg_tags(self, tags: Union[m_tag.PrsTagEntry, str, List[str], List[m_tag.PrsTagEntry]]):
        if isinstance(tags, (str, m_tag.PrsTagEntry)):
            tags = [tags]

        for tag in tags:
            if isinstance(tag, str):
                tag_entry = m_tag.PrsTagEntry(id=tag)
            else:
                tag_entry = tag
            svc.ldap.add_alias(parent_dn=self.tags_node, aliased_dn=tag_entry.dn, name=tag_entry.id)

            svc.set_tag_cache(tag_entry, "data_storage", self._format_data_store(tag_entry.data.attributes.dict()))
