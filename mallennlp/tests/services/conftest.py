import pytest

from mallennlp.services.db import _get_db, init_tables


@pytest.fixture(scope="module")
def db():
    db = _get_db(":memory:")
    init_tables(db)
    yield db
    db.close()
