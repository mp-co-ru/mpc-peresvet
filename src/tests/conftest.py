import pytest
import os
import json
from starlette.testclient import TestClient

from app.main import app
from app.models.Tag import PrsTagCreate
from app.models.DataStorage import PrsDataStorageCreate

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client  # testing happens here

@pytest.fixture(scope='function')
def create_vm_default_datastorage(test_app):
    data = PrsDataStorageCreate()
    data.attributes.prsDefault = True
    data.attributes.prsEntityTypeCode = 1
    data.attributes.prsJsonConfigString = json.dumps({"putUrl": "http://vm:8428/api/put", "getUrl": "http://vm:8428/api/v1/export"})
    yield test_app.app.create_dataStorage(data)

@pytest.fixture(scope='function')
def create_tag(test_app, create_vm_default_datastorage):
    create_vm_default_datastorage
    yield test_app.app.create_tag(PrsTagCreate())
