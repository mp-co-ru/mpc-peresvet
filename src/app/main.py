import os
from app.api import tags
from app.api import dataStorages
from app.api import data
from app.PrsApplication import PrsApplication

app = PrsApplication(title='Peresvet')
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(dataStorages.router, prefix="/dataStorages", tags=["dataStorages"])
app.include_router(data.router, prefix="/data", tags=["data"])

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

