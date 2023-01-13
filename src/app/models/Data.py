from typing import List
from pydantic import BaseModel, Field

class PrsDataItem(BaseModel):
    x: int | str = Field(None, title="Метка времени",
       description="Может быть либо целым числом, в этом случае это микросекунды")
    y: int | float | dict | str = Field(None, title="Значение тега")
    q: int = Field(None, title="Код качества")

class PrsTagData(BaseModel):
    tagId: str
    data: List[PrsDataItem]

class PrsData(BaseModel):
    data: List[PrsTagData]
