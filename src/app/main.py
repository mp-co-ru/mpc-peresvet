from fastapi import FastAPI
from ldap_db import conn

from app.api import tags

app = FastAPI()

@app.on_event("startup")
async def startup():
    conn.bind()

@app.on_event("shutdown")
async def shutdown():
    conn.unbind()


app.include_router(tags.router)
