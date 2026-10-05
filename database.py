from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_DIR = Path(__file__).resolve().parent
engine = create_engine(
    f"sqlite:///{PROJECT_DIR / 'database.db'}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db


def initialize_database():
    from models.memo import Memo
    Base.metadata.create_all(engine)
