from fastapi import APIRouter
from fastapi import Request

router = APIRouter()

@router.get("/tags")
async def pong(req: Request):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    req.app.logger.error("Here Is Your Error Log")
    return {"tags": "yes!"}
