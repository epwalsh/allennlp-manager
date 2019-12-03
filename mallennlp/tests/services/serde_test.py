from typing import List, Optional

import pytest

from mallennlp.exceptions import InvalidPageParametersError
from mallennlp.services.serde import serde, serialize, deserialize, from_url


@serde
class Inner:
    x: str
    y: str


@serde
class Outer:
    a: int
    b: Inner
    c: List[Inner]


def test_encode_and_decode():
    o = Outer(1, Inner(x="1", y="2"), [Inner("3", "4")])
    assert o.a == 1
    assert o.b.x == "1"
    assert o.b.y == "2"
    s = serialize(o)  # type: ignore
    assert deserialize(Outer, s) == o  # type: ignore


def test_ignore_unknown_flag():
    @serde
    class StrictParams:
        a: Optional[int] = None

    with pytest.raises(InvalidPageParametersError) as e:
        from_url(StrictParams, "?foo=1", ignore_unknown=False)
    assert "unexpected parameter foo" in str(e.value)

    @serde
    class NonStrictParams:
        a: Optional[int] = None

    from_url(NonStrictParams, "?foo=1")


def test_str_param():
    @serde
    class Params:
        p: str

    params = from_url(Params, "?p=1")
    assert params.p == "1"
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_str_param():
    @serde
    class Params:
        p: Optional[str] = None

    params = from_url(Params, "?p=1")
    assert params.p == "1"
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_str_param():
    @serde
    class Params:
        p: List[str]

    params = from_url(Params, "?p=1")
    assert params.p == ["1"]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_str_param():
    @serde
    class Params:
        p: Optional[List[str]] = None

    params = from_url(Params, "?p=1")
    assert params.p == ["1"]
    params = from_url(Params, "")
    assert params.p is None


def test_int_param():
    @serde
    class Params:
        p: int

    params = from_url(Params, "?p=1")
    assert params.p == 1
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_int_param():
    @serde
    class Params:
        p: Optional[int] = None

    params = from_url(Params, "?p=1")
    assert isinstance(params.p, int)
    assert params.p == 1
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_int_param():
    @serde
    class Params:
        p: List[int]

    params = from_url(Params, "?p=1")
    assert params.p == [1]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_int_param():
    @serde
    class Params:
        p: Optional[List[int]] = None

    params = from_url(Params, "?p=1")
    assert params.p == [1]
    params = from_url(Params, "")
    assert params.p is None


def test_float_param():
    @serde
    class Params:
        p: float

    params = from_url(Params, "?p=1")
    assert params.p == 1.0
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_float_param():
    @serde
    class Params:
        p: Optional[float] = None

    params = from_url(Params, "?p=1")
    assert isinstance(params.p, float)
    assert params.p == 1.0
    params = from_url(Params, "")
    assert params.p is None


def test_list_of_float_param():
    @serde
    class Params:
        p: List[float]

    params = from_url(Params, "?p=1")
    assert params.p == [1.0]
    with pytest.raises(InvalidPageParametersError):
        from_url(Params, "")


def test_optional_list_of_float_param():
    @serde
    class Params:
        p: Optional[List[float]] = None

    params = from_url(Params, "?p=1")
    assert params.p == [1.0]
    params = from_url(Params, "")
    assert params.p is None


def test_bool_param():
    @serde
    class Params:
        p: bool

    params = from_url(Params, "?p=true")
    assert params.p is True
    params = from_url(Params, "?p=false")
    assert params.p is False


def test_optional_bool_param():
    @serde
    class Params:
        p: Optional[bool] = None

    params = from_url(Params, "?p=true")
    assert params.p is True
    params = from_url(Params, "?p=false")
    assert params.p is False
    params = from_url(Params, "")
    assert params.p is None


def test_from_url_and_serialize():
    @serde
    class Params:
        a: int

    params = from_url(Params, "?a=1")
    assert params.a == 1
    assert params == deserialize(Params, serialize(params))
