import os
from app.api import tags
from app.PrsApplication import PrsApplication

app = PrsApplication(title='Peresvet')
app.include_router(tags.router, prefix="/tags", tags=["tags"])   

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

