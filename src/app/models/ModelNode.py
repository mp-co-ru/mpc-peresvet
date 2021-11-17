from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, WritableEntry, BASE
from uuid import uuid4
from pydantic import BaseModel
from typing import List

from app.svc.Services import Services as svc

class PrsModelNodeAttrs(BaseModel):
    """Pydantic BaseModel for prsBaseModel attributes
    """
    cn: str = None
    description: List[str] = None 
    prsSystemNode: bool = None
    prsEntityTypeCode: int = None
    prsJsonConfigString: str = None
    prsIndex: int = None
    prsDefault: bool = None
    prsActive: bool = None
    prsApp: List[str] = None

class PrsModelNodeCreate(BaseModel):
    """Class for http requests validation"""
    parentId: str = svc.config["LDAP_BASE_NODE"]
    attributes: PrsModelNodeAttrs = PrsModelNodeAttrs()

class PrsResponseCreate(BaseModel):
    """Response for POST-request for entity creation"""
    id: str

class PrsModelNodeEntry:
    objectClass: str = 'prsModelNode'
        
    def __init__(self, data: PrsModelNodeCreate):
        conn = svc.ldap.get_read_conn()
        ldap_cls_def = ObjectDef(self.__class__.objectClass, conn)
        reader = Reader(conn, ldap_cls_def, data.parentId)
        reader.search()
        writer = Writer.from_cursor(reader)
        if data.attributes.cn is None:
            data.attributes.cn = str(uuid4())
        self.entry = writer.new('cn={},{}'.format(data.attributes.cn, data.parentId))
        for key, value in data.attributes.__dict__.items():
            if value is not None:
                self.entry[key] = value
        self.entry.entry_commit_changes()
        reader = Reader(conn, ldap_cls_def, self.entry.entry_dn, get_operational_attributes=True)
        reader.search()
        self.entry = reader[0]
        self.add_subnodes()        

    def get_id(self) -> str:        
        return str(self.entry.OA_entryUUID)
            
    def add_subnodes(self) -> None:
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










