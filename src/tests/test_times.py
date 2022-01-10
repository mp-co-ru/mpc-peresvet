import pytest
import app.times as t

@pytest.mark.parametrize(
    "payload, res",
    [
        [0, 0],
        ["1970-01-01 00:00:00", 0],
        ["1970-01-01 00:00:00+03:00", -10800000000],
        ["1970-01-01 03:00:00+03:00", 0]
    ],
)
def test_timestamp_to_int(payload, res):
    assert t.timestamp_to_int(payload) == res