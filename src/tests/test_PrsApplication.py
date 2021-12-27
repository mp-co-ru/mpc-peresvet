import pytest
from app.svc.Services import Services as svc

@pytest.mark.asyncio
async def test_reg_tag(create_vm_default_datastorage, create_tag):
    vm = create_vm_default_datastorage
    assert svc.data_storages, "There are no datastorages in cache."
    tag = create_tag
    assert svc.tags, "There are no tags in cache."
    
    assert svc.tags[tag.id]['app']['dataStorageId'] == vm.id
    assert svc.tags[tag.id]['data_storage']['metric'] == "t_{}".format(tag.data.attributes.cn.replace('-', '_'))
