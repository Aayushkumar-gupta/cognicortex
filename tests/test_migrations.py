from alembic import command
from alembic.config import Config

from app.db.base import Base
from app.db.session import engine


def test_migrations_match_models():
    config = Config(toml_file="pyproject.toml")
    Base.metadata.drop_all(bind=engine)

    command.upgrade(config, "head")
    command.check(config)
    command.downgrade(config, "base")
