import pytest
import os
from starlette.testclient import TestClient
import mock

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MOCK_SYNC, LEVEL
from app.main import app

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)    
    yield client  # testing happens here
