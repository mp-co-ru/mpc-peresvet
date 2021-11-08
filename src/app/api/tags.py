from fastapi import APIRouter
from fastapi.logger import logger

router = APIRouter()

@router.get("/tags")
async def pong():
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    logger.info("Houston, we have a %s", "interesting problem", exc_info=False)
    logger.info("Houston, we have a %s", "interesting problem", exc_info=True)
    return {"tags": "yes!"}
