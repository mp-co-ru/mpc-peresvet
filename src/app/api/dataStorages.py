from fastapi import APIRouter
import app.main as main
from app.models.ModelNode import PrsResponseCreate
from app.models.DataStorage import PrsDataStorageCreate

router = APIRouter()

@router.post("/", response_model=PrsResponseCreate, status_code=201)
async def create(payload: PrsDataStorageCreate):
    ds = await main.app.create_dataStorage(payload)
    id_ = ds.get_id()
    return {"id": id_}

@router.get("/{id}/", response_model=PrsDataStorageCreate)
async def read_DataStorage(id: str):
    ds = await main.app.read_dataStorage(id)
    return ds.data
