from typing import List, Union, Dict
import json

from urllib.parse import urlparse
from pydantic import validator, Field, root_validator
from ldap3 import LEVEL, DEREF_SEARCH, ALL_ATTRIBUTES

from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeCreateAttrs, PrsModelNodeEntry, PrsModelNodeCreate
from app.models.Tag import PrsTagEntry
from app.const import CN_DS_VICTORIAMETRICS, CN_DS_POSTGRESQL

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
    @classmethod
    def check_vm_config(cls, values):

        def uri_validator(x):
            try:
                result = urlparse(x)
                return all([result.scheme, result.netloc])
            except Exception as _:
                return False

        type_code = values.get('prsEntityTypeCode')
        if type_code == 1:
            config = values.get('prsJsonConfigString')
            if config is not None:
                try:
                    if isinstance(config, dict):
                        js = config
                    else:
                        js = json.loads(config)
                    put_url = js['putUrl']
                    get_url = js['getUrl']
                    if uri_validator(put_url) and uri_validator(get_url):
                       return values
                except Exception as _:
                    pass

            raise ValueError((
                "Конфигурация (атрибут prsJsonConfigString) для Victoriametrics должна быть вида:\n"
                "{'putUrl': 'http://<server>:<port>/api/put', 'getUrl': 'http://<server>:<port>/api/v1/export'}"
            ))
        else:
            return values

class PrsDataStorageCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsDataStorageCreateAttrs = PrsDataStorageCreateAttrs(prsEntityTypeCode=CN_DS_POSTGRESQL)

    @validator('parentId', check_fields=False, always=True)
    @classmethod
    def parentId_must_be_none(cls, v):
        if v is not None:
            raise ValueError('parentId must be null for dataStorage')
        return v

class PrsDataStorageEntry(PrsModelNodeEntry):
    '''Базовый класс для всех хранилищ'''
    objectClass: str = 'prsDataStorage'
    payload_class = PrsDataStorageCreate
    default_parent_dn: str = svc.config["LDAP_DATASTORAGES_NODE"]

    def __init__(self, **kwargs):
        super(PrsDataStorageEntry, self).__init__(**kwargs)

        self.tags_node = f"cn=tags,{self.dn}"
        self._read_tags()

    def _format_data_store(self, tag: PrsTagEntry) -> Union[None, Dict]:
        res = tag.data.attributes.prsStore
        if res is not None:
            try:
                res = json.loads(tag.data.attributes.prsStore)
            except Exception as _:
                pass

        return res

    def _read_tags(self):

        result, _, response, _ = svc.ldap.get_read_conn().search(
            search_base=self.tags_node,
            search_filter='(cn=*)', search_scope=LEVEL,
            dereference_aliases=DEREF_SEARCH,
            attributes=[ALL_ATTRIBUTES, 'entryUUID'])
        if not result:
            svc.logger.info(f"Нет привязанных тэгов к хранилищу '{self.data.attributes.cn}'")
            return

        for item in response:
            tag_entry = PrsTagEntry(id=str(item['attributes']['entryUUID']))
            svc.set_tag_cache(tag_entry, "data_storage", self._format_data_store(tag_entry))

        svc.logger.info(f"Тэги, привязанные к хранилищу `{self.data.attributes.cn}`, прочитаны.")

    async def connect(self): pass

    async def set_data(self, data): pass

    async def get_data(self, Any):  pass

    def _add_subnodes(self) -> None:
        data = PrsModelNodeCreate()
        data.parentId = self.id
        data.attributes = PrsModelNodeCreateAttrs(cn='tags')
        PrsModelNodeEntry(data=data)

        data.attributes.cn = 'alerts'
        PrsModelNodeEntry(data=data)

    def reg_tags(self, tags: Union[PrsTagEntry, str, List[str], List[PrsTagEntry]]):
        if isinstance(tags, (str, PrsTagEntry)):
            tags = [tags]

        for tag in tags:
            if isinstance(tag, str):
                tag_entry = PrsTagEntry(id=tag)
            else:
                tag_entry = tag
            svc.ldap.add_alias(parent_dn=self.tags_node, aliased_dn=tag_entry.dn, name=tag_entry.id)

            tag_store = self._format_data_store(tag_entry)
            if (tag_entry.data.attributes.prsStore is None) or (not tag_store == json.loads(tag_entry.data.attributes.prsStore)):
                tag_entry.modify({
                    "prsStore": json.dumps(tag_store)
                })

            svc.set_tag_cache(tag_entry, "data_storage", tag_store)
