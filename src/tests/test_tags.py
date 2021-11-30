import json
import uuid
import pytest

@pytest.mark.parametrize(
    "payload, status_code, res",
    [
        [{}, 201, {id: ""}]
    ],
)
def test_tag_add(test_app, payload, status_code, res):
    response = test_app.post("/tags", data=json.dumps(payload))
    assert response.status_code == status_code
    try: 
        uuid.UUID(response.json()['id'])
    except:
        assert False, "There is no UUID returned as tag id"  
    

