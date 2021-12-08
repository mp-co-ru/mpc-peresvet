from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsTagCreateAttrs(PrsModelNodeAttrs):
    """Attributes for request for /tags/ POST"""
    
    """top"""
    prsValueTypeCode: int = 0 
    prsSource: str = None
    prsStore: str = None 
    prsMeasureUnits: str = None
    prsMaxDev: float = None
    prsMaxLineDev: float = None
    prsArchive: bool = True
    prsCompress: bool = True 
    prsValueScale: float = None
    prsStep: bool = False
    prsUpdate: bool = True
    prsDefaultValue: str = None

class PrsTagCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    parentId: str = None
    dataSourceId: str = None
    attributes: PrsTagCreateAttrs = PrsTagCreateAttrs()

class PrsTagEntry(PrsModelNodeEntry):
    payload_class = PrsTagCreate
    objectClass: str = 'prsTag'
    default_parent_dn: str = "cn=tags,{}".format(svc.config["LDAP_BASE_NODE"])
    
    
    