from mallennlp.services.serialization import serializable


@serializable
class SerializableInner:
    x: str
    _y: str


@serializable
class SerializableOuter:
    a: int
    b: SerializableInner


def test_encode_and_decode():
    o = SerializableOuter(1, SerializableInner(x="1", y="2"))
    assert o.a == 1
    assert o.b.x == "1"
    assert o.b._y == "2"
    s = o.serialize()  # type: ignore
    assert SerializableOuter.deserialize(s) == o  # type: ignore
