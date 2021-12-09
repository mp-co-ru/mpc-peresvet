from typing import Optional
from pydantic import BaseModel

class D(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = 0

h = {'x':5}
d = D(**h)

print(d.dict(exclude_unset=True))