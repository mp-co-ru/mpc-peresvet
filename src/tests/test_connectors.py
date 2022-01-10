import uuid
from app.models.Connector import PrsConnectorCreate, PrsConnectorEntry

def test_connector_create():
    data = PrsConnectorCreate()
    conn = PrsConnectorEntry(data=data)
    try:
        uuid.UUID(conn.id)
    except ValueError as ex:
        assert False, ex

    conn_copy = PrsConnectorEntry(id=conn.id)
    assert conn_copy.id == conn.id