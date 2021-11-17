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

    def _add_subnodes(self) -> None:
        pass
    
    def _load(self, id: str = None, dn: str = None) -> None:
        conn = svc.ldap.get_read_conn()
        ldap_cls_def = ObjectDef(self.__class__.objectClass, conn)
        ldap_cls_def += ['entryUUID']
        if dn:
            reader = Reader(conn, ldap_cls_def, dn, get_operational_attributes=True)
        else:
            reader = Reader(conn, ldap_cls_def, svc.config["LDAP_BASE_NODE"], get_operational_attributes=True, query='entryUUID: {}'.format(id))

        reader.search()
        self.entry = reader[0]        

    def __init__(self, data: PrsModelNodeCreate = None, id: str = None):
        self.data = PrsModelNodeCreate()
        if id is None:
            conn = svc.ldap.get_read_conn()
            ldap_cls_def = ObjectDef(self.__class__.objectClass, conn)
            reader = Reader(conn, ldap_cls_def, data.parentId)
            reader.search()
            writer = Writer.from_cursor(reader)
            if data.attributes.cn is None:
                data.attributes.cn = str(uuid4())
            entry = writer.new('cn={},{}'.format(data.attributes.cn, data.parentId))
            for key, value in data.attributes.__dict__.items():
                if value is not None:
                    entry[key] = value
                self.data[key] = value
            entry.entry_commit_changes()
            self._load(dn = entry.entry_dn)
            self._add_subnodes()
        else: 
            self._load(id=id)

    def get_id(self) -> str:        
        return str(self.entry.OA_entryUUID)
            
    

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










