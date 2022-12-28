import os
import json

import pytest
from starlette.testclient import TestClient

from app.main import app
from app.models.Tag import PrsTagCreate
from app.models.DataStorage import PrsDataStorageCreate

@pytest.fixture(scope="module")
@pytest.mark.asyncio
async def test_app():
    async with TestClient(app) as client:
        yield client  # testing happens here

@pytest.fixture(scope='function')
@pytest.mark.asyncio
async def create_vm_default_datastorage(test_app):
    data = PrsDataStorageCreate()
    data.attributes.prsDefault = True
    data.attributes.prsEntityTypeCode = 1
    data.attributes.prsJsonConfigString = json.dumps({"putUrl": "http://vm:8428/api/put", "getUrl": "http://vm:8428/api/v1/export"})
    async with test_app.app.create_dataStorage(data) as ds:
        yield ds

@pytest.fixture(scope='function')
@pytest.mark.asyncio
async def create_tag(test_app, create_vm_default_datastorage):
    #await create_vm_default_datastorage
    async with test_app.app.create_tag(PrsTagCreate()) as new_tag:
        yield new_tag
