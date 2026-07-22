from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import settings
from storage.models import Base

engine = create_engine(settings.database_url, echo=False)


def init_db():
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
