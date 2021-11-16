from fastapi import APIRouter
from fastapi import Request
import json
import app.models.models as m
from app.svc.Services import Services as svc

router = APIRouter()

@router.post("/", response_model=m.PrsResponseCreate, status_code=201)
async def create(payload: m.PrsTagCreate):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    svc.logger.debug(payload)
    return {"id": "yes!"}

