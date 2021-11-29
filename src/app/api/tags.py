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
    new_tag = PrsTagEntry(svc.ldap.get_write_conn(), payload)
    return {"id": new_tag.get_id()}

@router.get("/{id}/", response_model=PrsTagCreate)
async def read_tag(id: str):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    svc.logger.debug("Working!")
    tag = PrsTagEntry(svc.ldap.get_read_conn(), id=id)
    return tag.data

