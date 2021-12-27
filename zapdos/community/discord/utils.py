import datetime
from typing import Dict, List, Type, TypedDict, _TypedDictMeta


class Snowflake(int):
    @property
    def timestamp(self) -> int:
        """Milliseconds since Discord Epoch, the first second of 2015 or 1420070400000."""
        DISCORD_EPOCH = 1420070400000
        return int(self >> 22) + DISCORD_EPOCH

    @property
    def internal_worker_id(self) -> int:
        return int(self & 0x3E0000) >> 17

    @property
    def internal_process_id(self) -> int:
        return int(self & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        return int(self & 0xFFF)

    def to_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp)

    def __add__(self, _) -> None:
        raise NotImplementedError

    def __iadd__(self, _) -> None:
        raise NotImplementedError

    def __sub__(self, _) -> None:
        raise NotImplementedError

    def __isub__(self, _) -> None:
        raise NotImplementedError

    def __mul__(self, _) -> None:
        raise NotImplementedError

    def __imul__(self, _) -> None:
        raise NotImplementedError

    def __truediv__(self, _) -> None:
        raise NotImplementedError

    def __itruediv__(self, _) -> None:
        raise NotImplementedError

    def __floordiv__(self, _) -> None:
        raise NotImplementedError

    def __ifloordiv__(self, _) -> None:
        raise NotImplementedError


def get_best_file_format(acccepted: List[str], prefered: List[str]) -> str:
    for fmt in prefered:
        if fmt in acccepted:
            return fmt
    else:
        return acccepted[0]


def transform_typed_dict(dict_: Dict, typed_dict: Type[TypedDict]) -> Dict:
    """Recursively transform a dict into a typed dict."""
    transformed_dict = {
        k: typed_dict.__annotations__.get(k)(
            transform_typed_dict(v, typed_dict.__annotations__[k])
        )
        if k in typed_dict.__annotations__
        and type(typed_dict.__annotations__[k]) == _TypedDictMeta
        else (typed_dict.__annotations__.get(k)(v) if k in typed_dict.__annotations__ else v)
        for k, v in dict_.items()
    }
    return transformed_dict
