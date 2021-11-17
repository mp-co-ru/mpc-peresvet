from fastapi import APIRouter
from fastapi import Request
import json
from app.models.ModelNode import PrsResponseCreate
from app.models.Tag import PrsTagCreate, PrsTagEntry
from app.svc.Services import Services as svc

router = APIRouter()

@router.post("/", response_model=PrsResponseCreate, status_code=201)
async def create(payload: PrsTagCreate):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    new_tag = PrsTagEntry(payload)
    return {"id": new_tag.get_id()}


