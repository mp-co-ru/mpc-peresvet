from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, BASE
from uuid import uuid4
from pydantic import BaseModel
from typing import List

from app.svc.Services import Services
from app.models.models import PrsBaseModelCreate, PrsTagCreate

class PrsModelNodeEntry(Entry):
    objectClass: str = 'prsModelNode'
        
    @classmethod
    def cast(cls, some_entry: Entry):
        """Cast an A into a B."""
        assert isinstance(some_entry, Entry)
        some_entry.__class__ = cls
        return some_entry

    @classmethod
    def create(cls, data: PrsBaseModelCreate):
        conn = Services.ldap.get_read_conn()
        ldap_cls_def = ObjectDef(cls.objectClass, conn)
        reader = Reader(conn, ldap_cls_def, data.parentId)
        reader.search()
        writer = Writer.from_cursor(reader)
        if data.attributes.cn is None:
            data.attributes.cn = uuid4()
        n_e = writer.new('cn={},{}'.format(data.attributes.cn, data.parentId))
        for key, value in data.attributes.__dict__.items():
            if value is not None:
                n_e[key] = value
        n_e.entry_commit_changes()
        cls.add_subnodes(n_e)
        return cls.cast(n_e)
    
    @classmethod
    def add_subnodes(cls, entry: Entry) -> None:
        pass

'''
def pr_obj():
    conn = Services.ldap.get_read_conn()
    o = ObjectDef('prsModelNode', conn)
    r = Reader(conn, o, 'cn=tags,cn=prs')
    r.search()
    w = Writer.from_cursor(r)
    n_e = w.new('cn=tag1,cn=tags,cn=prs')
    n_e.uniqueIdentifier = str(uuid4())
    n_e.entry_commit_changes()
    Services.logger.info(o)
'''










