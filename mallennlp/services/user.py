from typing import Optional

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

    def find(self, username: str, password: str):
        self.cursor.execute("SELECT * FROM user WHERE username=?", (username))
        result = self.cursor.fetchone()
        if not result:
            return None
        if not check_password_hash(result["password"], password):
            return None
        return User(**result)

    def create(self, username: str, password: str):
        password = generate_password_hash(password, method="sha256")
        self.cursor.execute(
            "INSERT INTO user (alt_id, username, password) VALUES (?, ?, ?)",
            (0, username, password),
        )
        self.db.commit()
