import json
import uuid
import pytest
from mock import patch
from app.models.DataStorage import PrsDataStorageEntry, PrsDataStorageCreate
from app.svc.Services import Services as svc

def test_PrsDataStorage():
    try:
        new_dataStorage = PrsDataStorageEntry(conn=svc.ldap.get_write_conn(), data=PrsDataStorageCreate())
    except:
        assert False, "Fail while creating new dataStorage."

    try:
        uuid.UUID(new_dataStorage.id)
    except:
        assert False, "DataStorage id is not UUID."

    dataStorage_id = new_dataStorage.id
    try:
        dataStorage = PrsDataStorageEntry(conn=svc.ldap.get_read_conn(), id=dataStorage_id)
    except:
        assert False, "Fail while load tag."

    assert dataStorage.id == dataStorage_id
