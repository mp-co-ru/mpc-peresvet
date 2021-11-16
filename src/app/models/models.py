from pydantic import create_model, BaseModel
from typing import List

TagAttributes = None
class PrsTagCreate(BaseModel):
    parentId: str = None
    dataSourceId: str = None
    dataStorageId: str = None
    attributes: TagAttributes