from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union
from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsDataStorageCreateAttrs(PrsModelNodeAttrs):
    """
    Атрибуты сущности `dataStorage`.
    Используются при создании/изменении/получении хранилищ данных.
    """
    prsEntityTypeCode: int = Field(None, title='Код типа сущности',
        description=(
            '- 1 - Victoriametrics'
        )
    )
    
class PrsDataStorageCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsDataStorageCreateAttrs = PrsDataStorageCreateAttrs()

class PrsDataStorageEntry(PrsModelNodeEntry):
    objectClass: str = 'prsDataStorage'
    payload_class = PrsDataStorageCreate
    default_parent_dn: str = "cn=dataStorages,{}".format(svc.config["LDAP_BASE_NODE"])
    
    