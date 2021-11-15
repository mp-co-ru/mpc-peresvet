from fastapi import APIRouter
from fastapi import Request
import json
from app.ldap.model_node import pr_obj, pr_obj2

router = APIRouter()

@router.get("/tags")
async def pong(req: Request):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    pr_obj()
    return {"tags": "yes!"}

@router.get("/m")
async def move(req: Request):
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    pr_obj2()
    return {"tags": "yes"}
