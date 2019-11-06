from mallennlp.domain.user import User
from mallennlp.services.db import get_db_from_app


class UserService:
    def __init__(self):
        self.db = get_db_from_app()

    def get(self, userid: str) -> User:
        _id, alt_id = userid.split(" ")
        return User(int(_id), int(alt_id), "admin", "password")
