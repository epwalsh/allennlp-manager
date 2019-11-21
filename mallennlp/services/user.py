from typing import Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash

from mallennlp.domain.user import User
from mallennlp.services.db import get_db_from_app, Tables


MIN_PASSWORD_LENGTH = 8


class UserService:
    def __init__(self, db=None):
        if not db:
            db = get_db_from_app()
        self.db = db
        self.cursor = self.db.cursor()

    def get(self, userid: str) -> Optional[User]:
        _id, alt_id = [int(x) for x in userid.split(" ")]
        self.cursor.execute(
            f"SELECT * FROM {Tables.USERS.value} WHERE id=? AND alt_id=?", (_id, alt_id)
        )
        result = self.cursor.fetchone()
        if result:
            return User(**result)
        return None

    @staticmethod
    def check_password(user: User, password: str) -> bool:
        return check_password_hash(user.password, password)

    def find(
        self, username: str, password: str = None, check_password: bool = True
    ) -> Optional[User]:
        self.cursor.execute(
            f"SELECT * FROM {Tables.USERS.value} WHERE username=?", (username,)
        )
        result = self.cursor.fetchone()
        if not result:
            return None
        if check_password and not check_password_hash(result["password"], password):
            return None
        return User(**result)

    def create(self, username: str, password: str):
        password = generate_password_hash(password, method="sha256")
        self.cursor.execute(
            f"INSERT INTO {Tables.USERS.value} (alt_id, username, password) VALUES (?, ?, ?)",
            (0, username, password),
        )
        self.db.commit()

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, "password not long enough"
        if password.isalpha() or password.isnumeric():
            return False, "password must be a mix of letters and numbers and/or symbols"
        return True, None

    def changepw(self, username: str, password: str) -> bool:
        hashed_password = generate_password_hash(password, method="sha256")
        self.cursor.execute(
            f"UPDATE {Tables.USERS.value} SET password=?, alt_id = alt_id + 1 WHERE username=?",
            (hashed_password, username),
        )
        self.db.commit()
        return self.find(username, password) is not None
