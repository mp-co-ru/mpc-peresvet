import os
from fastapi import FastAPI
from app.api import tags
from app.svc.Services import Services

app = FastAPI(title='Peresvet', debug=False)

@app.on_event("startup")
async def startup():
    Services.set_logger()
    Services.set_ldap()


@app.on_event("shutdown")
async def shutdown():
    pass

app.include_router(tags.router, prefix="/tags", tags=["tags"])   
