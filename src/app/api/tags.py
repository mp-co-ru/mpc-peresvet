from fastapi import APIRouter
from fastapi import Request
import json
import app.main as main
from app.models.ModelNode import PrsResponseCreate
from app.models.Tag import PrsTagCreate
from app.svc.Services import Services as svc

router = APIRouter()

@router.post("/", response_model=PrsResponseCreate, status_code=201)
async def create(payload: PrsTagCreate):
    id = main.app.create_tag(payload).get_id()
    return {"id": id}

@router.get("/{id}/", response_model=PrsTagCreate)
async def read_tag(id: str):
    return main.app.read_tag(id).form_get_response()

