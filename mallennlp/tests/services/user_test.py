import pytest

from mallennlp.domain.user import Permissions
from mallennlp.services.user import UserService


@pytest.fixture(scope="module")
def service(db):
    return UserService(db)


@pytest.fixture(scope="module")
def get_larbear(service):
    service.create(
        "larbear",
        "password123",
        fullname="Larry Barry",
        nickname="Larbear",
        role="Engineer",
        email="larbear@gmail.com",
        phone="555-123-1234",
        permissions=Permissions.READ_WRITE,
    )

    def get_him():
        return service.find("larbear", "password123")

    return get_him


def test_create_user(get_larbear):
    user = get_larbear()
    assert user is not None
    assert user.fullname == "Larry Barry"
    assert user.nickname == "Larbear"
    assert user.role == "Engineer"
    assert user.email == "larbear@gmail.com"
    assert user.phone == "555-123-1234"
    assert user.permissions == Permissions.READ_WRITE


def test_change_username(service, get_larbear):
    user = get_larbear()
    service.change_username(user, "larbear12")
    assert get_larbear() is None
    user = service.find("larbear12", "password123")
    assert user is not None
    # Change back.
    service.change_username(user, "larbear")


def test_delete_user(service, get_larbear):
    service.delete_user(get_larbear())
    assert get_larbear() is None
