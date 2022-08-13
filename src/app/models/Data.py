from pydantic import BaseModel, Field
from typing import List, Union

class PrsDataItem(BaseModel):
    x: Union[int, str] = Field(None, title="Метка времени",
       description="Может быть либо целым числом, в этом случае это наносекунды")
    y: Union[None, float, int, dict, str]
    q: int = None

class PrsTagData(BaseModel):
    tagId: str
    data: List[PrsDataItem]

class PrsData(BaseModel):
    data: List[PrsTagData]
