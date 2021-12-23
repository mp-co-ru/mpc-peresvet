import app.api.tags as tags
import app.api.dataStorages as dataStorages
import app.api.data as data
import app.PrsApplication as prsapp

app = prsapp.PrsApplication(title='Peresvet')
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(dataStorages.router, prefix="/dataStorages", tags=["dataStorages"])
app.include_router(data.router, prefix="/data", tags=["data"])

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

