from pydantic import BaseModel
from typing import List
from app.svc.Services import Services as svc

class PrsBaseModel(BaseModel):
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

class PrsResponseCreate(BaseModel):
    """Response for /tags/ POST"""
    id: str

class PrsTagCreateAttrs(PrsBaseModel):
    """Attributes for request for /tags/ POST"""
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

class PrsTagCreate(BaseModel):
    """Request /tags/ POST"""
    parentId: str = svc.config["LDAP_BASE_NODE"]
    dataSourceId: str = None
    attributes: PrsTagCreateAttrs
        


    