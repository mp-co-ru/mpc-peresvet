from fastapi import APIRouter
from fastapi import Request
import app.main as main
import app.models.ModelNode as ModelNode
import app.models.Tag as Tag

router = APIRouter()

@router.post("/", response_model=ModelNode.PrsResponseCreate, status_code=201)
async def create(payload: Tag.PrsTagCreate):
    id = main.app.create_tag(payload).get_id()
    return {"id": id}

@router.get("/{id}/", response_model=Tag.PrsTagCreate)
async def read_tag(id: str):
    return main.app.read_tag(id).data
