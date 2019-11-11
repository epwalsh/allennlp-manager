import inspect
import json
from typing import Dict, Any

import attr


@attr.s
class Serializable:
    """
    An attrs class that is serializable to JSON.
    """

    @classmethod
    def from_default(cls, default):
        """
        Decode the `default()` representation into an instance.
        """
        fields = attr.fields_dict(cls)
        params: Dict[str, Any] = {}
        for param_name, param_value in default.items():
            field_attr = fields[param_name]
            field_type = field_attr.type

            # Private fields should be instantiated without leading '_'.
            if param_name.startswith("_"):
                param_name = param_name[1:]

            # If field is type is Serializable, call `from_default` on the params dict.
            if (
                field_type is not None
                and inspect.isclass(field_type)
                and issubclass(field_type, Serializable)
            ):
                params[param_name] = field_type.from_default(param_value)
            else:
                params[param_name] = param_value
        return cls(**params)  # type: ignore

    def default(self) -> Any:
        """
        Return a representation that is JSON serializable.
        """
        return attr.asdict(self, recurse=False, retain_collection_types=False)

    def encode(self) -> str:
        class Encoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Serializable):
                    return o.default()
                return json.JSONEncoder.default(self, o)

        return Encoder().encode(self)

    @classmethod
    def decode(cls, s: str):
        return cls.from_default(json.loads(s))
