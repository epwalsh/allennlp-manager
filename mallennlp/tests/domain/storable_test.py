import attr

from mallennlp.domain.storable import Storable


@attr.s(auto_attribs=True)
class StorableInner(Storable):
    x: str
    _y: str


@attr.s(auto_attribs=True)
class StorableOuter(Storable):
    a: int
    b: StorableInner


def test_load_store_and_dump_store():
    o = StorableOuter(a=1, b=StorableInner(x="1", y="2"))
    s = o.dump_store()
    assert s == {"a": 1, "b": {"x": "1", "_y": "2"}}
    assert StorableOuter.load_store(s) == o
