import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, String, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker, declarative_base

# Load backend/.env into the process environment. This has to happen here,
# before DATABASE_URL (and every other os.environ.get() call anywhere else
# in the app — recipe_generator, nutrition_lookup, vision_recognition, etc.)
# is read, because this module is the first thing every entry point
# (uvicorn app.main:app, scripts/init_db.py, pytest) imports.
#
# Pointed at an explicit path (backend/.env, i.e. two directories up from
# this file: app/db.py -> app/ -> backend/) rather than relying on
# load_dotenv()'s default cwd-search behavior, so this works the same
# whether you run commands from backend/ or from the project root.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/deepchef"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GUID(TypeDecorator):
    """
    Portable UUID column: uses Postgres' native UUID type in production,
    and a CHAR(36) string in SQLite (used only by the test suite's
    in-memory DB — see tests/conftest.py). Lets the same models work
    against both without duplicating table definitions.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()