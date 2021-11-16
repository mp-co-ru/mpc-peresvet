from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, BASE
from uuid import uuid4
from pydantic import BaseModel
from typing import List

from app.svc.Services import Services


class Prs_ldap_ModelNode(Entry):
    objectClass: str = 'prsModelNode'
        
    @classmethod
    def cast(cls, some_entry: Entry):
        """Cast an A into a B."""
        assert isinstance(some_entry, Entry)
        some_entry.__class__ = cls
        return some_entry

    @classmethod
    def init(cls, class_name: str):
        cls.objectClass = class_name












