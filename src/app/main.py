from fastapi import WebSocket, WebSocketDisconnect
from app.svc.Services import Services as svc
from app.PrsApplication import PrsApplication
import app.api.tags as tags
import app.api.dataStorages as dataStorages
import app.api.data as data

app = PrsApplication(title='Peresvet')

app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(dataStorages.router, prefix="/dataStorages", tags=["dataStorages"])
app.include_router(data.router, prefix="/data", tags=["data"])

@app.websocket("/{connector_id}")
async def websocket_endpoint(websocket: WebSocket, connector_id: int):
    await svc.ws_pool.connect(websocket)
    try:
        while True:
            pass
            '''
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
            '''
    except WebSocketDisconnect:
        svc.ws_pool.disconnect(websocket)
        '''
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
        '''


@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

