from fastapi import APIRouter
from fastapi import Request
import json
import app.main as main
from app.models.Data import PrsData
from app.svc.Services import Services as svc

router = APIRouter()

@router.post("/", status_code=200)
async def data_set(payload: PrsData):
    main.app.data_set(payload)

    