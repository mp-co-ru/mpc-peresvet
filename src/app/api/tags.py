from fastapi import APIRouter
from fastapi import Request
import json

router = APIRouter()

@router.get("/tags")
async def pong(req: Request):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    req.app.logger.info("Logger")
    return {"tags": "yes!"}
