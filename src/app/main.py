from fastapi import WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
import json

from app.svc.Services import Services as svc
from app.PrsApplication import PrsApplication
import app.api.tags as tags
import app.api.dataStorages as dataStorages
import app.api.data as data
import app.api.connectors as connectors

app = PrsApplication(title='Peresvet')

app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(dataStorages.router, prefix="/dataStorages", tags=["dataStorages"])
app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(connectors.router, prefix="/connectors", tags=["connectors"])

@app.websocket("/{connector_id}")
async def websocket_endpoint(websocket: WebSocket, connector_id: str):
    try:
        await svc.ws_pool.connect(websocket)

        svc.logger.info("Установлена связь с коннектором {}".format(connector_id))

        response = {}
        try:
            response = app.response_to_connector(connector_id)
        except HTTPException as ex:
            svc.logger.info(ex.detail)
            await websocket.send_text(ex.detail)
            await websocket.close()
            raise WebSocketDisconnect()            

        await websocket.send_json(response)
        while True:
            pass
            '''
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
            '''
    except WebSocketDisconnect:
        svc.ws_pool.disconnect(websocket)
        svc.logger.info("Разрыв связи с коннектором {}".format(connector_id))
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

