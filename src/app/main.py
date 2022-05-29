import json
import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException

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

#TODO:
# 1. вынести код работы с вебсокетом в отдельный файл, сделать по типу строк выше
# 2. разобраться с таймаутами пинг-понга. параметры в командной строке при запуске приложения не работают!
@app.websocket("/{connector_id}")
async def websocket_endpoint(websocket: WebSocket, connector_id: str):
    try:
        await svc.ws_pool.connect(websocket)

        svc.logger.info(f"Установлена связь с коннектором {connector_id}")

        response = {}
        try:
            response = app.response_to_connector(connector_id)
        except HTTPException as ex:
            er_str = f"Ошибка при установлении связи с коннектором {connector_id}: {ex}"
            svc.logger.info(er_str)
            await websocket.send_text(er_str)
            await websocket.close()
            raise WebSocketDisconnect() from ex

        await websocket.send_json(response)

        while True:
            received_data = await websocket.receive_json()
            app.data_set(data=received_data)
            await websocket.send_text(f"Вы послали: {received_data}")

    except Exception as ex:
        svc.ws_pool.disconnect(websocket)
        svc.logger.info(f"Разрыв связи с коннектором {connector_id}: {ex}")


@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass
