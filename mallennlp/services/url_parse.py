from typing import Dict, List, Any, Union

import attr
import urllib.parse as urlparse

from mallennlp.exceptions import InvalidPageParametersError


class ParamParser:
    ALLOWED_TYPES = {
        str,
        Union[str, type(None)],
        List[str],
        Union[List[str], type(None)],
        int,
        Union[int, type(None)],
        List[int],
        Union[List[int], type(None)],
        float,
        Union[float, type(None)],
        List[float],
        Union[List[float], type(None)],
        bool,
        Union[bool, type(None)],
    }

    def __init__(self, params_cls, ignore_unknown: bool = True):
        self.params_cls = params_cls
        self.ignore_unknown = ignore_unknown
        self.params_attrs = attr.fields_dict(self.params_cls)
        self.required_params: List[str] = []
        for param_name, param_attr in self.params_attrs.items():
            if param_attr.default == attr.NOTHING:
                self.required_params.append(param_name)
            param_type = param_attr.type
            if param_type not in self.ALLOWED_TYPES:
                raise TypeError(
                    f"invalid page parameter type {param_name}: {param_type}"
                )

    def parse(self, raw_params: Dict[str, List[str]]):
        for required_param in self.required_params:
            if required_param not in raw_params:
                raise InvalidPageParametersError(
                    f"missing required page parameter {required_param}"
                )
        init_params: Dict[str, Any] = {}
        for param_name, raw_param in raw_params.items():
            if param_name not in self.params_attrs:
                if self.ignore_unknown:
                    continue
                else:
                    raise InvalidPageParametersError(
                        f"unexpected parameter {param_name}"
                    )
            param_type = self.params_attrs[param_name].type
            value: Any
            if param_type in (str, Union[str, type(None)]):
                if len(raw_param) > 1:
                    raise InvalidPageParametersError(
                        f"expected single value for {param_name}"
                    )
                value = raw_param[0]
            elif param_type in (List[str], Union[List[str], type(None)]):
                value = raw_param
            elif param_type in (int, Union[int, type(None)]):
                if len(raw_param) > 1:
                    raise InvalidPageParametersError(
                        f"expected single value for {param_name}"
                    )
                try:
                    value = int(raw_param[0])
                except TypeError:
                    raise InvalidPageParametersError(
                        f"expected int type for {param_name}"
                    )
            elif param_type in (List[int], Union[List[int], type(None)]):
                try:
                    value = [int(p) for p in raw_param]
                except TypeError:
                    raise InvalidPageParametersError(
                        f"expected int type for {param_name}"
                    )
            elif param_type in (float, Union[float, type(None)]):
                if len(raw_param) > 1:
                    raise InvalidPageParametersError(
                        f"expected single value for {param_name}"
                    )
                try:
                    value = float(raw_param[0])
                except TypeError:
                    raise InvalidPageParametersError(
                        f"expected float type for {param_name}"
                    )
            elif param_type in (List[float], Union[List[float], type(None)]):
                try:
                    value = [float(p) for p in raw_param]
                except TypeError:
                    raise InvalidPageParametersError(
                        f"expected float type for {param_name}"
                    )
            elif param_type in (bool, Union[bool, type(None)]):
                if len(raw_param) > 1:
                    raise InvalidPageParametersError(
                        f"expected single value for {param_name}"
                    )
                bool_str = raw_param[0].lower()
                if bool_str == "true":
                    value = True
                elif bool_str == "false":
                    value = False
                else:
                    raise InvalidPageParametersError(
                        f"expected 'true' or 'false' for {param_name}"
                    )
            else:
                raise NotImplementedError
            init_params[param_name] = value
        return self.params_cls(**init_params)


def from_url(maybe_cls=None, ignore_unknown: bool = True):
    def wrap(cls):
        if not attr.has(cls):
            cls = attr.s(auto_attribs=True, slots=True)(cls)
        parser = ParamParser(cls, ignore_unknown=ignore_unknown)

        @classmethod  # type: ignore
        def from_url(cls, url: str):
            raw_params: Dict[str, List[str]] = urlparse.parse_qs(
                urlparse.urlparse(url).query
            )
            return parser.parse(raw_params)

        cls.from_url = from_url
        return cls

    if maybe_cls is None:
        return wrap
    return wrap(maybe_cls)
