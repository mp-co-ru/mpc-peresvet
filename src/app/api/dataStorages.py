from fastapi import APIRouter
import app.main as main
import app.models.ModelNode as m_mn 
import app.models.DataStorage as m_ds

router = APIRouter()

@router.post("/", response_model=m_mn.PrsResponseCreate, status_code=201)
async def create(payload: m_ds.PrsDataStorageCreate):
    id = main.app.create_dataStorage(payload).get_id()
    return {"id": id}

@router.get("/{id}/", response_model=m_ds.PrsDataStorageCreate)
async def read_DataStorage(id: str):
    return main.app.read_dataStorage(id).data
    

