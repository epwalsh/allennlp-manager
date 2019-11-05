from flask_login import UserMixin, AnonymousUserMixin


class User(UserMixin):
    @classmethod
    def get(cls, userid: str) -> "User":
        return User()


class AnonymousUser(AnonymousUserMixin):
    pass
