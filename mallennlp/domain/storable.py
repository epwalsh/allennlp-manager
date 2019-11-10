import inspect
from typing import Dict, Any

import attr


@attr.s
class Storable:
    @classmethod
    def load_store(cls, data: Dict[str, Any]):
        """
        Recursively initialize `Storable`(s) from store data.
        """
        fields = attr.fields_dict(cls)
        params: Dict[str, Any] = {}
        for param_name, param_value in data.items():
            field_attr = fields[param_name]
            field_type = field_attr.type

            # Private fields should be instantiated without leading '_'.
            if param_name.startswith("_"):
                param_name = param_name[1:]

            # If field is of type Storable, call `load_store` on the params dict.
            if (
                field_type is not None
                and inspect.isclass(field_type)
                and issubclass(field_type, Storable)
            ):
                params[param_name] = field_type.load_store(param_value)
            else:
                params[param_name] = param_value
        return cls(**params)  # type: ignore

    def dump_store(self) -> Dict[str, Any]:
        return attr.asdict(self)
