from enum import IntEnum
from typing import List

class CNDataStorageTypes(IntEnum):
    CN_DS_VICTORIAMETRICS : int = 1
    CN_DS_POSTGRESQL : int = 0

    @classmethod
    def get_supported(cls) -> List[int]:
        return [cls.CN_DS_VICTORIAMETRICS, cls.CN_DS_POSTGRESQL]

class CNHTTPExceptionCodes(IntEnum):
    CN_500 : int = 500

class CNTagValueTypes(IntEnum):
    CN_INT: int = 1
    CN_DOUBLE: int = 2
    CN_STR: int = 3
    CN_JSON: int = 4
