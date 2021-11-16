from pydantic import BaseModel
from typing import List

class PrsResponseCreate(BaseModel):
    id: str

class PrsTagCreateAttrs(BaseModel):
    cn: str = None
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
    description: List[str] = None
    prsSystemNode: bool = None
    prsEntityTypeCode: int = None
    prsJsonConfigString: dict = None
    prsIndex: int = None
    prsDefault: bool = None
    prsActive: bool = True
    prsApp: List[str] = None
class PrsTagCreate(BaseModel):
    parentId: str = None
    dataSourceId: str = None
    attributes: PrsTagCreateAttrs
        


    