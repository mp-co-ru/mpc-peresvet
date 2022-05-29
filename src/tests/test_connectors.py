import pytest
import uuid
from app.models.Connector import PrsConnectorCreate, PrsConnectorEntry
from fastapi import HTTPException

def test_connector_create():
    data = PrsConnectorCreate()
    conn = PrsConnectorEntry(data=data)
    try:
        uuid.UUID(conn.id)
    except ValueError as ex:
        assert False, ex

    conn_copy = PrsConnectorEntry(id=conn.id)
    assert conn_copy.id == conn.id

def test_wrong_connector_id():
    id = str(uuid.uuid4())
    with pytest.raises(HTTPException):
        conn = PrsConnectorEntry(id=id)
