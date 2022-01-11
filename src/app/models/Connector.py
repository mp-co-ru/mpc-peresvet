from pydantic import validator, Field, root_validator
from typing import List, Union, Dict
import json
from ldap3 import LEVEL, DEREF_SEARCH, ALL_ATTRIBUTES
from urllib.parse import urlparse

from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeCreateAttrs, PrsModelNodeEntry, PrsModelNodeCreate
from app.models.Tag import PrsTagEntry
from app.const import *

class PrsConnectorCreateAttrs(PrsModelNodeCreateAttrs):
    """
    Атрибуты сущности `connector`.
    Используются при создании/изменении/получении коннекторов.
    """
    pass
    
class PrsConnectorCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsConnectorCreateAttrs = PrsConnectorCreateAttrs()

    @validator('parentId', check_fields=False, always=True)
    def parentId_must_be_none(cls, v):
        if v is not None:
            raise ValueError('parentId must be null for connector')
        return v

class PrsConnectorEntry(PrsModelNodeEntry):
    objectClass: str = 'prsConnector'
    payload_class = PrsConnectorCreate
    default_parent_dn: str = svc.config["LDAP_CONNECTORS_NODE"]

    def __init__(self, **kwargs):
        super(PrsConnectorEntry, self).__init__(**kwargs)
        
        self.tags_node = "cn=tags,{}".format(self.dn)        
   
    def _add_subnodes(self) -> None:
        data = PrsModelNodeCreate()
        data.parentId = self.id
        data.attributes = PrsModelNodeCreateAttrs(cn='tags')
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
           