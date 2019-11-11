import attr

from mallennlp.services.serialization import Serializable


@attr.s(auto_attribs=True)
class SerializableInner(Serializable):
    x: str
    _y: str


@attr.s(auto_attribs=True)
class SerializableOuter(Serializable):
    a: int
    b: SerializableInner


def test_encode_and_decode():
    o = SerializableOuter(a=1, b=SerializableInner(x="1", y="2"))
    s = o.encode()
    assert SerializableOuter.decode(s) == o
