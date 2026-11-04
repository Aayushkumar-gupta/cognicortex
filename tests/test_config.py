import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_short_secret_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL="sqlite://", SECRET_KEY="too-short")
