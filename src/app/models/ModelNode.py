from ldap3 import Connection, ObjectDef, Reader, Writer, Entry, WritableEntry, BASE, SUBTREE
from uuid import uuid4, UUID
from pydantic import BaseModel, validator
from typing import List, Optional

from app.svc.Services import Services as svc

class PrsModelNodeAttrs(BaseModel):
    """Pydantic BaseModel for prsBaseModel attributes
    """
    cn: Optional[List[str]] = None
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
    parentId: str = None # uuid of parent node
    attributes: PrsModelNodeAttrs = PrsModelNodeAttrs()
    
    @validator('parentId')
    def parentId_must_be_uuid(cls, v):
        try:
            UUID(v)
        except:
            raise ValueError('parentId must be uuid')
        return v.title()

class PrsResponseCreate(BaseModel):
    """Response for POST-request for entity creation"""
    id: str

class PrsModelNodeEntry:
    payload_class: None
    objectClass: str = 'prsModelNode'
    default_parent_dn: str = svc.config["LDAP_BASE_NODE"]

    def _add_subnodes(self) -> None:
        pass
    
    def _load(self, id: str = None, dn: str = None) -> None:
        ldap_cls_def = ObjectDef(self.__class__.objectClass, self.conn)
        ldap_cls_def += ['entryUUID']
        if dn is not None:
            reader = Reader(self.conn, ldap_cls_def, dn, get_operational_attributes=True)
        else:
            reader = Reader(self.conn, ldap_cls_def, self.__class__.default_parent_dn, get_operational_attributes=True, query='entryUUID: {}'.format(id))

        reader.search()
        self.entry = reader[0] 

    @classmethod
    def _get_node_dn(cls, conn: Connection, id: str) -> str:
        found = conn.search(
            search_base=cls.default_parent_dn,
            search_filter="(entryUUID={})".format(id),
            search_scope=SUBTREE,
            dereference_aliases=False,
            attributes=['cn']
        )

        return conn.response[0]['dn'] if found else None
    
    @classmethod
    def _get_node_id(cls, conn: Connection, dn: str) -> str:
        ldap_cls_def = ObjectDef(cls.objectClass, conn)
        ldap_cls_def += ['entryUUID']
        reader = Reader(conn, ldap_cls_def, dn, get_operational_attributes=True)
        reader.search()
        return str(reader[0].entryUUID)

    def __init__(self, conn: Connection, data: PrsModelNodeCreate = None, id: str = None):
        self.conn = conn
        self.payload_class = data.__class__
        if id is None:
            ldap_cls_def = ObjectDef(self.__class__.objectClass, self.conn)
            if data.parentId is None:
                self.parent_dn = self.__class__.default_parent_dn
                self.parent_id = self.__class__._get_node_id(conn, self.parent_dn)
            else:
                self.parent_id = data.parentId
                self.parent_dn = self.__class__._get_node_dn(conn, data.parentId)
                
            reader = Reader(self.conn, ldap_cls_def, self.parent_dn)
            reader.search()
            writer = Writer.from_cursor(reader)
            entry = writer.new('cn={},{}'.format((data.attributes.cn, str(uuid4()))[data.attributes.cn is None], self.parent_dn))
            for key, value in data.attributes.__dict__.items():
                if value is not None:
                    entry[key] = value
            entry.entry_commit_changes()
            self._load(dn = entry.entry_dn)
            self._add_subnodes()
        else: 
            self._load(id=id)

    def get_id(self) -> str:        
        return str(self.entry.entryUUID)

    def _add_fields_to_get_response(self, data): 
        pass

    def form_get_response(self):
        data = self.payload_class()
        attrs = self.entry.entry_to_json(include_empty=False)
        attrs.pop("dn")
        attrs.pop("objectClass")
        data.attributes = attrs
        data.parentId = self.parent_id
        self._add_fields_to_get_response(data)
        return data
    
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