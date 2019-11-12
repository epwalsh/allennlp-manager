from typing import List, Optional, Any

import pytest

from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.url_parse import from_url
from mallennlp.services.serialization import serializable


def test_invalid_type_raises():
    with pytest.raises(TypeError):

        @from_url
        class BadParams:
            x: Any


def test_ignore_unknown_flag():
    @from_url(ignore_unknown=False)
    class StrictParams:
        a: Optional[int] = None

    with pytest.raises(InvalidPageParametersError) as e:
        StrictParams.from_url("?foo=1")
    assert "unexpected parameter foo" in str(e.value)

    @from_url(ignore_unknown=True)
    class NonStrictParams:
        a: Optional[int] = None

    NonStrictParams.from_url("?foo=1")


def test_str_param():
    @from_url
    class Params:
        p: str

    params = Params.from_url("?p=1")
    assert params.p == "1"
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_str_param():
    @from_url
    class Params:
        p: Optional[str] = None

    params = Params.from_url("?p=1")
    assert params.p == "1"
    params = Params.from_url("")
    assert params.p is None


def test_list_of_str_param():
    @from_url
    class Params:
        p: List[str]

    params = Params.from_url("?p=1")
    assert params.p == ["1"]
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_list_of_str_param():
    @from_url
    class Params:
        p: Optional[List[str]] = None

    params = Params.from_url("?p=1")
    assert params.p == ["1"]
    params = Params.from_url("")
    assert params.p is None


def test_int_param():
    @from_url
    class Params:
        p: int

    params = Params.from_url("?p=1")
    assert params.p == 1
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_int_param():
    @from_url
    class Params:
        p: Optional[int] = None

    params = Params.from_url("?p=1")
    assert isinstance(params.p, int)
    assert params.p == 1
    params = Params.from_url("")
    assert params.p is None


def test_list_of_int_param():
    @from_url
    class Params:
        p: List[int]

    params = Params.from_url("?p=1")
    assert params.p == [1]
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_list_of_int_param():
    @from_url
    class Params:
        p: Optional[List[int]] = None

    params = Params.from_url("?p=1")
    assert params.p == [1]
    params = Params.from_url("")
    assert params.p is None


def test_float_param():
    @from_url
    class Params:
        p: float

    params = Params.from_url("?p=1")
    assert params.p == 1.0
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_float_param():
    @from_url
    class Params:
        p: Optional[float] = None

    params = Params.from_url("?p=1")
    assert isinstance(params.p, float)
    assert params.p == 1.0
    params = Params.from_url("")
    assert params.p is None


def test_list_of_float_param():
    @from_url
    class Params:
        p: List[float]

    params = Params.from_url("?p=1")
    assert params.p == [1.0]
    with pytest.raises(InvalidPageParametersError):
        Params.from_url("")


def test_optional_list_of_float_param():
    @from_url
    class Params:
        p: Optional[List[float]] = None

    params = Params.from_url("?p=1")
    assert params.p == [1.0]
    params = Params.from_url("")
    assert params.p is None


def test_bool_param():
    @from_url
    class Params:
        p: bool

    params = Params.from_url("?p=true")
    assert params.p is True
    params = Params.from_url("?p=false")
    assert params.p is False


def test_optional_bool_param():
    @from_url
    class Params:
        p: Optional[bool] = None

    params = Params.from_url("?p=true")
    assert params.p is True
    params = Params.from_url("?p=false")
    assert params.p is False
    params = Params.from_url("")
    assert params.p is None


def test_from_url_and_serialize():
    @from_url
    @serializable
    class Params:
        a: int

    params = Params.from_url("?a=1")
    assert params.a == 1
    assert params == Params.deserialize(params.serialize())
