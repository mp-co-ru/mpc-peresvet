import os
from fastapi import FastAPI
from app.api import tags
from app.svc.Services import Services

def create_app() -> FastAPI:
        
    app = FastAPI(title='Peresvet', debug=False)
    return app

app = create_app()

Services.set_logger()
app.logger = Services.logger
Services.set_ldap()

app.include_router(tags.router)   
