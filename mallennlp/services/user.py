from typing import Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash

from mallennlp.domain.user import User
from mallennlp.services.db import get_db_from_app


class UserService:
    def __init__(self, db=None):
        if not db:
            db = get_db_from_app()
        self.db = db
        self.cursor = self.db.cursor()

    def get(self, userid: str) -> Optional[User]:
        _id, alt_id = [int(x) for x in userid.split(" ")]
        self.cursor.execute("SELECT * FROM user WHERE id=? AND alt_id=?", (_id, alt_id))
        result = self.cursor.fetchone()
        if result:
            return User(**result)
        return None

    def find(
        self, username: str, password: str = None, check_password: bool = True
    ) -> Optional[User]:
        self.cursor.execute("SELECT * FROM user WHERE username=?", (username,))
        result = self.cursor.fetchone()
        if not result:
            return None
        if check_password and not check_password_hash(result["password"], password):
            return None
        return User(**result)

    def create(self, username: str, password: str):
        password = generate_password_hash(password, method="sha256")
        self.cursor.execute(
            "INSERT INTO user (alt_id, username, password) VALUES (?, ?, ?)",
            (0, username, password),
        )
        self.db.commit()

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        if len(password) < 8:
            return False, "password must be at least 8 characters"
        if "password" in password:
            return False, "password cannot contain the word 'password'"
        return True, None

    def changepw(self, username: str, password: str) -> bool:
        hashed_password = generate_password_hash(password, method="sha256")
        self.cursor.execute(
            "UPDATE user SET password=? WHERE username=?", (hashed_password, username)
        )
        self.db.commit()
        return self.find(username, password) is not None
