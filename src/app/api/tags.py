from fastapi import APIRouter
from fastapi import Request
import json
import app.models.models as m

router = APIRouter()

@router.post("/", status_code=201)
async def pong(payload: m.PrsTagCreate):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    
    return {"tags": "yes!"}

