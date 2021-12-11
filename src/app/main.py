import os
from app.api import tags
from app.api import dataStorages
from app.PrsApplication import PrsApplication

app = PrsApplication(title='Peresvet')
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(dataStorages.router, prefix="/dataStorages", tags=["dataStorages"])

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

