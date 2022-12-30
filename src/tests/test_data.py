import json
import pytest

from fastapi import Response

from app.models.DataStorage import PrsDataStorageCreate
from app.models.Data import PrsData
from app.svc.Services import Services as svc
from app.models.data_storages.vm import PrsVictoriametricsEntry
from app.models.Tag import PrsTagCreate

@pytest.mark.asyncio
async def test_data_set(test_app, create_vm_default_datastorage, monkeypatch):
    vm = await create_vm_default_datastorage

    async def mock_set_data(*args):
        assert args[0] == {tag.id: [(0, 0, 0)]}
        return Response(content="ok", status_code=200)

    monkeypatch.setattr(vm, 'set_data', mock_set_data)

    # [{"data": [{"tagId": "test_tag_1", "data": [{"x": 0, "y": 0, "q": 0}]}]}, {"test_tag_1": [(0, 0, 0)]}]

    tag_data = PrsTagCreate()
    tag_data.dataStorageId = vm.id
    tag_data.attributes.cn = "test_tag_1"
    tag = await test_app.app.create_tag(tag_data)

    data = [{"tagId": tag.id, "data": [{"x": 0, "y": 0, "q": 0}]}]

    p_data = PrsData(data=data)

    await test_app.app.data_set(data=p_data)
