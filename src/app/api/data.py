from fastapi import APIRouter
from fastapi import Request
import json
import app.main as main
import app.models.Data as Data

router = APIRouter()

@router.post("/", status_code=200)
async def data_set(payload: Data.PrsData):
    return await main.app.data_set(payload)
