from __future__ import annotations

from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

from models.user import User
from models.prediction import MLPrediction
from models.ml_task import MLTask


def _create_engine():
    settings = get_settings()
    db_url = settings.DATABASE_URL

    return create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True,
    )


engine = _create_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Зависимость для FastAPI
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(drop_all: bool = False) -> None:
    if drop_all:
        SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)