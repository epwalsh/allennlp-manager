from typing import Optional, Tuple, Iterable

from werkzeug.security import check_password_hash, generate_password_hash

from mallennlp.domain.user import User, Permissions
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

    def create(
        self,
        username: str,
        password: str,
        fullname: str = None,
        nickname: str = None,
        role: str = None,
        email: str = None,
        phone: str = None,
        permissions: Permissions = Permissions.READ,
    ):
        password = generate_password_hash(password, method="sha256")
        permissions_level = int(permissions)
        self.cursor.execute(
            f"INSERT INTO {Tables.USERS.value} "
            "(alt_id, username, password, fullname, nickname, role, email, phone, permissions_level) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                0,
                username,
                password,
                fullname,
                nickname,
                role,
                email,
                phone,
                permissions_level,
            ),
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

    def set_permissions(
        self, username: str, permissions: Permissions
    ) -> Optional[User]:
        permissions_level = int(permissions)
        self.cursor.execute(
            f"UPDATE {Tables.USERS.value} SET permissions_level=? WHERE username=?",
            (permissions_level, username),
        )
        self.db.commit()
        return self.find(username, check_password=False)

    def update_user(
        self,
        user: User,
        fields: Tuple[str, ...] = ("fullname", "nickname", "role", "email", "phone"),
    ):
        set_clause = ", ".join(f"{field}=?" for field in fields)
        field_values = tuple(getattr(user, field) for field in fields)
        self.cursor.execute(
            f"UPDATE {Tables.USERS.value} SET {set_clause} WHERE username=?",
            field_values + (user.username,),
        )
        self.db.commit()

    def change_username(self, user: User, new_username: str):
        self.cursor.execute(
            f"UPDATE {Tables.USERS.value} SET username=?, alt_id = alt_id +1 WHERE username=?",
            (new_username, user.username),
        )
        self.db.commit()

    def delete_by_username(self, username: str):
        self.cursor.execute(
            f"DELETE FROM {Tables.USERS.value} WHERE username=?", (username,)
        )
        self.db.commit()

    def delete_user(self, user: User):
        self.delete_by_username(user.username)

    def iter_usernames(self) -> Iterable[str]:
        cursor = self.db.execute(f"SELECT username FROM {Tables.USERS.value}", [])
        return (row["username"] for row in cursor)
