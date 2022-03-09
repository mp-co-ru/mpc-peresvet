from fastapi import APIRouter
import app.main as main
from app.models.ModelNode import PrsResponseCreate
from app.models.Connector import PrsConnectorCreate

router = APIRouter()

@router.post("/", response_model=PrsResponseCreate, status_code=201)
async def create(payload: PrsConnectorCreate):
    id = main.app.create_connector(payload).get_id()
    return {"id": id}

@router.get("/{id}/", response_model=PrsConnectorCreate)
async def read_connector(id: str):
    return main.app.read_connector(id).data
    
