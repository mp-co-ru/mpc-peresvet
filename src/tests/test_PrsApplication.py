from app.main import app

def test_reg_tag(create_vm_default_datastorage, create_tag):
    vm = create_vm_default_datastorage
    tag = create_tag
    print(app.tags)
    assert app.tags[tag.id]['app']['dataStorageId'] == vm.id
    assert app.tags[tag.id]['data_storage']['metric'] == tag.data.attributes.cn
