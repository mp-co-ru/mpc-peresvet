def test_reg_tag(test_app, create_vm_default_datastorage, create_tag):
    vm = create_vm_default_datastorage
    assert test_app.app.data_storages, "There are no datastorages in cache."
    tag = create_tag
    assert test_app.app.tags, "There are no tags in cache."
    
    assert test_app.app.tags[tag.id]['app']['dataStorageId'] == vm.id
    assert test_app.app.tags[tag.id]['data_storage']['metric'] == tag.data.attributes.cn
