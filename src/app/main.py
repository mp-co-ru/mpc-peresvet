from fastapi import FastAPI

from app.api import tags

app = FastAPI()

app.include_router(tags.router)
