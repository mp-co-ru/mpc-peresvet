from fastapi import FastAPI
from app.api import tags
from app.logger.PrsLogger import PrsLogger

def create_app() -> FastAPI:
    app = FastAPI(title='Peresvet', debug=False)
    logger = PrsLogger.make_logger()
    app.logger = logger

    return app

app = create_app()
app.include_router(tags.router)
