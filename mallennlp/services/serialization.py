import inspect
import json
from typing import Dict, Any

import attr


class JsonSerializer(json.JSONEncoder):
    """
    Adds a serializable default representation for `attr` classes.
    """

    def default(self, o):
        if attr.has(o):
            return attr.asdict(o, recurse=False, retain_collection_types=False)
        return json.JSONEncoder.default(self, o)


def from_default(cls, default):
    """
    Initialize attr object from it's default representation.
    """
    fields = attr.fields_dict(cls)
    params: Dict[str, Any] = {}
    for param_name, param_value in default.items():
        field_attr = fields[param_name]
        field_type = field_attr.type

        # Private fields should be instantiated without leading '_'.
        if param_name.startswith("_"):
            param_name = param_name[1:]

        # Recursively initialize fields that are also `attr` objects.
        if (
            field_type is not None
            and inspect.isclass(field_type)
            and attr.has(field_type)
        ):
            params[param_name] = from_default(field_type, param_value)
        else:
            params[param_name] = param_value
    return cls(**params)


def serialize(self) -> str:
    """
    Encode a serializable object into a str.
    """
    return JsonSerializer().encode(self)


@classmethod  # type: ignore
def deserialize(cls, s: str):
    """
    Decode a serializable object from a str.
    """
    default = json.loads(s)
    return from_default(cls, default)


def serializable(cls):
    """
    Class decorator for creating serializable classes.
    """
    cls.serialize = serialize
    cls.deserialize = deserialize
    return attr.s(auto_attribs=True, slots=True)(cls)
