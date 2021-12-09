import json
import uuid
import pytest
from mock import patch
from app.models.Tag import PrsTagEntry, PrsTagCreate
from app.svc.ldap.ldap_db import PrsLDAP
from app.svc.Services import Services as svc
import ldap3

@pytest.mark.parametrize(
    "payload, status_code, res",
    [
        [{}, 201, {id: ""}]
    ],
)
def test_tag_add(test_app, payload, status_code, res):
    response = test_app.post("/tags/", data=json.dumps(payload))
    assert response.status_code == status_code
    try: 
        uuid.UUID(response.json()['id'])
    except:
        assert False, "There is no UUID returned as tag id"  

def test_tag_get(test_app):
    response = test_app.post("/tags/", data=json.dumps({}))
    tag_id = response.json()['id']
    response = test_app.get("/tags/{}".format(tag_id))
    assert response.status_code == 200

def test_PrsTag():
    try:
        new_tag = PrsTagEntry(conn=svc.ldap.get_write_conn(), data=PrsTagCreate())
    except:
        assert False, "Fail while creating new tag."

    try:
        uuid.UUID(new_tag.id)
    except:
        assert False, "Tag id is not UUID."

    tag_id = new_tag.id
    try:
        tag = PrsTagEntry(conn=svc.ldap.get_read_conn(), id=tag_id)
    except:
        assert False, "Fail while load tag."

    assert tag.id == tag_id

def test_f_35_cn_as_uuid():
    new_tag = PrsTagEntry(conn=svc.ldap.get_write_conn(), data=PrsTagCreate())
    assert new_tag.data.attributes.cn == [new_tag.id]

def test_add_tag_with_multiple_cn():
    data=PrsTagCreate()
    data.attributes.cn = ["имя 1", "имя 2"]
    try:
        new_tag = PrsTagEntry(conn=svc.ldap.get_write_conn(), data=data)
    except:
        assert False, "Tag with multiple cn is not created"
    
    assert new_tag.data.attributes.cn == data.attributes.cn
    