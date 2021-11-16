from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, BASE
from uuid import uuid4
from pydantic import BaseModel
from typing import List

from app.svc.Services import Services
from app.models.models import PrsTagCreate

class PrsModelNodeEntry(Entry):
    objectClass: str = 'prsModelNode'
        
    @classmethod
    def cast(cls, some_entry: Entry):
        """Cast an A into a B."""
        assert isinstance(some_entry, Entry)
        some_entry.__class__ = cls
        return some_entry

    @classmethod
    def create(cls, data: PrsTagCreate):
        conn = Services.ldap.get_read_conn()
        o = ObjectDef('prsModelNode', conn)
        r = Reader(conn, o, data.parentId)
        r.search()
        w = Writer.from_cursor(r)
        if data.attributes.cn is None:
            data.attributes.cn = uuid4()
        n_e = w.new('cn={},{}'.format(data.attributes.cn, data.parentId))
        n_e.entry_commit_changes()
        """Add attrs!!!"""
        return cls.cast(n_e)



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











