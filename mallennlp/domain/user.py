import attr
from flask_login import UserMixin, AnonymousUserMixin


@attr.s(auto_attribs=True)
class User(UserMixin):
    id: int
    alt_id: int
    username: str
    password: str

    def get_id(self) -> str:
        return f"{self.id} {self.alt_id}"


class AnonymousUser(AnonymousUserMixin):
    pass
