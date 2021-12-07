import pytest
import os
from starlette.testclient import TestClient
import mock

from app.main import app
from app.svc.ldap.ldap_db import PrsLDAP

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MOCK_SYNC, LEVEL

@pytest.fixture(scope="module")
def test_app():
    REAL_SERVER = os.getenv("LDAP_HOST")
    REAL_USER = os.getenv("LDAP_USER")
    REAL_PASSWORD = os.getenv("LDAP_PASSWORD")
    BASE_NODE = os.getenv("LDAP_BASE_NODE", "cn=prs")

    # Retrieve server info and schema from a real server
    server = Server(REAL_SERVER, get_info=ALL)
    connection = Connection(server, REAL_USER, REAL_PASSWORD, auto_bind=True)

    # Store server info and schema to json files
    server.info.to_file('server_info.json')
    server.schema.to_file('server_schema.json')

    # Read entries from a portion of the DIT from real server and store them in a json file
    if connection.search(BASE_NODE, '(objectclass=*)', search_scope=LEVEL, attributes=ALL_ATTRIBUTES):
        connection.response_to_file('server_entries.json', raw=True)

    # Close the connection to the real server
    connection.unbind()

    # Create a fake server from the info and schema json files
    fake_server = Server.from_definition('mock_server', 'server_info.json', 'server_schema.json')

    # Create a MockSyncStrategy connection to the fake server
    fake_connection = Connection(fake_server, user='cn=user,cn=prs', password='my_password', client_strategy=MOCK_SYNC)

    # Add a fake user for Simple binding
    fake_connection.strategy.add_entry('cn=prs', {'cn': 'prs', 'objectClass': 'prsModelNode'})

    # Populate the DIT of the fake server
    fake_connection.strategy.entries_from_json('server_entries.json')

    # Bind to the fake server
    fake_connection.bind()

    def new_read_conn(cls, **kwargs) -> Connection:
        return fake_connection
    
    def new_write_conn(cls, **kwargs) -> Connection:
        return fake_connection

    mock.patch.object(PrsLDAP, 'get_read_conn', new=new_read_conn)
    mock.patch.object(PrsLDAP, 'get_write_conn', new=new_write_conn)

    client = TestClient(app)
    yield client  # testing happens here
