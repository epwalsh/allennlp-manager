import enum
from typing import Optional

import attr
from flask_login import UserMixin, AnonymousUserMixin

from mallennlp.domain.dataclass import dataclass


@enum.unique
class Permissions(enum.IntEnum):
    NONE = 0
    READ = 1
    READ_WRITE = 2
    ADMIN = 3


@dataclass
class User(UserMixin):
    id: int
    alt_id: int
    username: str
    password: str
    fullname: Optional[str] = None
    nickname: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    permissions_level: int = attr.ib(default=1)

    def get_id(self) -> str:
        return f"{self.id} {self.alt_id}"

    @permissions_level.validator
    def validate_permissions_level(self, attribute, value):
        if not (1 <= value <= len(Permissions)):
            raise ValueError

    @property
    def permissions(self) -> Permissions:
        iter(Permissions)
        for i, p in enumerate(iter(Permissions)):
            if i == self.permissions_level:
                return p
        raise ValueError("Bad permissions level")


class AnonymousUser(AnonymousUserMixin):
    @property
    def permissions(self) -> Permissions:
        return Permissions.NONE
