from pydantic import BaseModel, validator, Field
from typing import List, Optional, Union

from app.svc.Services import Services as svc

class PrsDataItem(BaseModel):
    x: Union[str, int] = Field(None, title="Метка времени", 
       description="Может быть либо целым числом, в этом случае это наносекунды")
    y: Union[None, int, float, str, dict]
    q: int = None

class PrsTagData(BaseModel):
    tagId: str
    data: List[PrsDataItem]

class PrsData(BaseModel):
    data: List[PrsTagData]