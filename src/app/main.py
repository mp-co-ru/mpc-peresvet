import os
from fastapi import FastAPI
from app.api import tags
from app.svc.Services import Services

def create_app() -> FastAPI:
        
    app = FastAPI(title='Peresvet', debug=False)
    Services.set_logger()
    Services.set_ldap()

    return app

app = create_app()

app.include_router(tags.router)   
