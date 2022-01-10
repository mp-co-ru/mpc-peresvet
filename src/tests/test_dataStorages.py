import json
import uuid
import pytest
from app.models.DataStorage import PrsDataStorageCreate
from app.models.data_storages.vm import PrsVictoriametricsEntry
from app.svc.Services import Services as svc

@pytest.mark.parametrize(
    "payload, status_code, res",
    [
        [{}, 422, {id: ""}],
        [{"attributes": {"prsEntityTypeCode": 1}}, 422, {}],
        [{"parentId": str(uuid.uuid4())}, 422, {}],
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"url": "uncorrect url"}'}}, 422, {}],
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"url": "http://localhost"}'}}, 422, {}],
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"putUrl": "http://localhost", "getUrl": "http://localhost"}'}}, 201, {}]
    ],
)
def test_dataStorage_create(test_app, payload, status_code, res):
    response = test_app.post("/dataStorages/", data=json.dumps(payload))
    assert response.status_code == status_code
    
@pytest.mark.asyncio
async def test_dataStorage_connect():
    data = PrsDataStorageCreate()
    data.attributes.prsEntityTypeCode = 1
    data.attributes.prsJsonConfigString = json.dumps({"putUrl": "http://vm:8428", "getUrl": "http://vm:8428/api/v1/export"})
    vm = PrsVictoriametricsEntry(data=data)
    assert await vm.connect() == 200