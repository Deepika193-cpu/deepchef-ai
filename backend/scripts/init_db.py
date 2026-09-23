"""
Creates all tables from the SQLAlchemy models against DATABASE_URL.

NOTE: this is schema creation, not a real migrations tool. There's no
Alembic set up yet, so there's no versioned migration history or safe
upgrade/downgrade path — running this against a database that already
has data in a different shape will not migrate it for you. Fine for
first-time setup or a throwaway dev database; add Alembic before this
touches a database you care about.

Usage:
    cd backend
    python scripts/init_db.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import Base, engine
from app import models  # noqa: F401 — import registers all models on Base


def main():
    print(f"Creating tables on: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created (or already existed):")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    main()
