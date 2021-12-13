import datetime
from dateutil import tz, parser

# функция преобразовывает пришедшую метку времени в количество микросекунд
microsec = 1000000
def timestamp_to_int (field) -> int:
    timestampFrom = None

    if isinstance (field, (int,)):
        return field

    timestampFrom = field
    if isinstance (field, (str,)):
        timestampFrom = parser.parse (field)

    if timestampFrom.tzinfo is None:
        timestampFrom = timestampFrom.replace (tzinfo=datetime.timezone.utc)

    return int ((timestampFrom - datetime.datetime.fromtimestamp(0, datetime.timezone.utc)).total_seconds () * microsec)

def int_to_local_timestamp (int_ts: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int_ts / microsec, tz.tzlocal())

def now_int() -> int:
    now = datetime.datetime.now(tz.tzlocal())
    return timestamp_to_int(now)
