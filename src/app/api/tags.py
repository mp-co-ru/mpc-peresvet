from fastapi import APIRouter

router = APIRouter()


@router.get("/tags")
async def pong():
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    return {"tags": "yes!"}
