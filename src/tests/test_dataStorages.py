import json
import uuid
import pytest
from mock import patch
from app.models.DataStorage import PrsDataStorageEntry, PrsDataStorageCreate, PrsDataStorageCreateAttrs
from app.svc.Services import Services as svc

@pytest.mark.parametrize(
    "payload, status_code, res",
    [
        [{}, 201, {id: ""}],
        [{"attributes": {"prsEntityTypeCode": 1}}, 422, {}],
        [{"parentId": str(uuid.uuid4())}, 422, {}],
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"url": "uncorrect url"}'}}, 422, {}],
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"url": "http://localhost"}'}}, 422, {}]
        [{"attributes": {"prsEntityTypeCode": 1, "prsJsonConfigString": '{"putUrl": "http://localhost", "getUrl": "http://localhost"}'}}, 422, {}]
    ],
)
def test_dataStorage_create(test_app, payload, status_code, res):
    response = test_app.post("/dataStorages/", data=json.dumps(payload))
    assert response.status_code == status_code
    