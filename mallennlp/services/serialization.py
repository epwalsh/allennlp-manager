import inspect
import json
from typing import Dict, Any, List, Type, TypeVar

import attr


class JsonSerializer(json.JSONEncoder):
    """
    Adds a serializable default representation for `attr` classes.
    """

    def default(self, o):
        if attr.has(o):
            return attr.asdict(o, recurse=False, retain_collection_types=False)
        return json.JSONEncoder.default(self, o)


T = TypeVar("T")


def from_default(ObjType: Type[T], default: Any) -> T:
    """
    Initialize an object from it's default representation.
    """
    if not attr.has(ObjType):
        return default
    fields = attr.fields_dict(ObjType)
    params: Dict[str, Any] = {}
    for param_name, param_value in default.items():
        field_attr = fields[param_name]
        field_type = field_attr.type

        # Private fields should be instantiated without leading '_'.
        if param_name.startswith("_"):
            param_name = param_name[1:]

        # Recursively initialize fields that are also `attr` objects, otherwise
        # use the raw default `param_value`.
        if field_type is not None:
            if inspect.isclass(field_type) and attr.has(field_type):
                # Field type is an `attr` object.
                params[param_name] = from_default(field_type, param_value)
            elif getattr(field_type, "__origin__", None) in (List, list):
                # List of things, possibly other `attr` objects.
                subtype = field_type.__args__[0]
                params[param_name] = [from_default(subtype, val) for val in param_value]
            else:
                # Default to just using `param_value` as is.
                params[param_name] = param_value
        else:
            # Default to just using `param_value` as is.
            params[param_name] = param_value
    return ObjType(**params)  # type: ignore


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
