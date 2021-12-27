import datetime
import logging
import typing
from dateutil.parser import isoparse
from enum import EnumMeta

logger: logging.Logger = logging.getLogger(__name__)


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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"


def get_best_file_format(acccepted: typing.List[str], prefered: typing.List[str]) -> str:
    for fmt in prefered:
        if fmt in acccepted:
            return fmt
    else:
        return acccepted[0]


def transform_typed_dict(value: typing.Any, type_: typing.Any) -> typing.Dict:
    """Recursively transform a dict into a typed dict."""
    if value is None:
        return None
    elif isinstance(type_, typing._GenericAlias) and type_.__origin__ is typing.Union:
        # If the type is a typing Union, we want the first type.
        return transform_typed_dict(value, type_.__args__[0])
    elif isinstance(type_, typing._TypedDictMeta):
        # Value is a Typed typing.Dict, transform all key:values in it.

        for key in value.keys():
            if key not in type_.__annotations__:
                logger.warn(f"{key} is not a valid key in {type_.__name__}")
        return {
            key: transform_typed_dict(value, type_.__annotations__.get(key))
            for key, value in value.items()
        }
    elif isinstance(type_, typing._GenericAlias) and type_.__origin__ is list:
        return [transform_typed_dict(value, type_.__args__[0]) for value in value]
    elif isinstance(type_, typing._GenericAlias) and type_.__origin__ is dict:
        return {k: transform_typed_dict(v, type_.__args__[1]) for k, v in value.items()}
    elif type_ == Snowflake:
        return Snowflake(value)
    elif type_ == datetime.datetime:
        return isoparse(value)
    elif type_ == bool:
        return bool(value)
    elif isinstance(type_, EnumMeta):
        # We'll be passing the raw value here, this is fine.
        return value
    else:
        return value
