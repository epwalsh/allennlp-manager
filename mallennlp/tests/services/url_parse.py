from typing import List, Optional, Any

import pytest

from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.url_parse import url_params, from_url
from mallennlp.services.serialization import serializable, serialize, deserialize


def test_invalid_type_raises():
    with pytest.raises(TypeError):

        @url_params
        class BadParams:
            x: Any


def test_ignore_unknown_flag():
    @url_params
    class StrictParams:
        a: Optional[int] = None

    with pytest.raises(InvalidPageParametersError) as e:
        from_url(StrictParams, "?foo=1", ignore_unknown=False)
    assert "unexpected parameter foo" in str(e.value)

    @url_params
    class NonStrictParams:
        a: Optional[int] = None

    from_url(NonStrictParams, "?foo=1")


def test_str_param():
    @url_params
    class Params:
        p: str

    params = from_url(Params, "?p=1")
    assert params.p == "1"
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_str_param():
    @url_params
    class Params:
        p: Optional[str] = None

    params = from_url(Params, "?p=1")
    assert params.p == "1"
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_str_param():
    @url_params
    class Params:
        p: List[str]

    params = from_url(Params, "?p=1")
    assert params.p == ["1"]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_str_param():
    @url_params
    class Params:
        p: Optional[List[str]] = None

    params = from_url(Params, "?p=1")
    assert params.p == ["1"]
    params = from_url(Params, "")
    assert params.p is None


def test_int_param():
    @url_params
    class Params:
        p: int

    params = from_url(Params, "?p=1")
    assert params.p == 1
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_int_param():
    @url_params
    class Params:
        p: Optional[int] = None

    params = from_url(Params, "?p=1")
    assert isinstance(params.p, int)
    assert params.p == 1
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_int_param():
    @url_params
    class Params:
        p: List[int]

    params = from_url(Params, "?p=1")
    assert params.p == [1]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_int_param():
    @url_params
    class Params:
        p: Optional[List[int]] = None

    params = from_url(Params, "?p=1")
    assert params.p == [1]
    params = from_url(Params, "")
    assert params.p is None


def test_float_param():
    @url_params
    class Params:
        p: float

    params = from_url(Params, "?p=1")
    assert params.p == 1.0
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_float_param():
    @url_params
    class Params:
        p: Optional[float] = None

    params = from_url(Params, "?p=1")
    assert isinstance(params.p, float)
    assert params.p == 1.0
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_float_param():
    @url_params
    class Params:
        p: List[float]

    params = from_url(Params, "?p=1")
    assert params.p == [1.0]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_float_param():
    @url_params
    class Params:
        p: Optional[List[float]] = None

    params = from_url(Params, "?p=1")
    assert params.p == [1.0]
    params = from_url(Params, "")
    assert params.p is None


def test_bool_param():
    @url_params
    class Params:
        p: bool

    params = from_url(Params, "?p=true")
    assert params.p is True
    params = from_url(Params, "?p=false")
    assert params.p is False


def test_optional_bool_param():
    @url_params
    class Params:
        p: Optional[bool] = None

    params = from_url(Params, "?p=true")
    assert params.p is True
    params = from_url(Params, "?p=false")
    assert params.p is False
    params = from_url(Params, "")
    assert params.p is None


def test_from_url_and_serialize():
    @url_params
    @serializable
    class Params:
        a: int

    params = from_url(Params, "?a=1")
    assert params.a == 1
    assert params == deserialize(Params, serialize(params))
