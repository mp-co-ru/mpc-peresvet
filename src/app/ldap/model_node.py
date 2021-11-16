from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, BASE
from uuid import uuid4
from pydantic import BaseModel, create_model
from typing import List

from app.svc.Services import Services

'''
class Prs_bm_ModelNode(BaseModel):
    cn: str
    description: List[str] = None
    prsSystemNode: bool = False
    prsEntityTypeCode: int = None
    prsJsonConfigString: str = None
    prsIndex: int = None
    prsDefault: bool = None
    prsActive: bool =  True
    prsApp: List[str] = None
'''

class Prs_ldap_ModelNode(Entry):
    objectClass: str = 'prsModelNode'
        
    @classmethod
    def cast(cls, some_entry: Entry):
        """Cast an A into a B."""
        assert isinstance(some_entry, Entry)
        some_entry.__class__ = cls
        return some_entry


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

def pr_obj2():    
    conn = Services.ldap.get_write_conn()
    o = ObjectDef('prsModelNode', conn)
    r = Reader(conn, o, 'cn=tag1,cn=tags,cn=prs')
    r.search()
    w = Writer.from_cursor(r)
    e = w[0]
    e.entry_move('cn=schedules,cn=prs')
    e.entry_commit_changes()
    Services.logger.info(e)
    