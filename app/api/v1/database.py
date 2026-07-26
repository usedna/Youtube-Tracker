from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends

from api.v1.config import settings
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = f"{settings.DB_SYSTEM}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    __table_args__ = {'extend_existing': True}
    schema = "public"
    
    @classmethod
    def get_or_create(cls, session, fkey=[], **kwargs):
        """Get an existing record or create a new one."""
        if fkey:
            filters = {key: kwargs[key] for key in fkey if key in kwargs}
            instance = session.query(cls).filter_by(**filters).first()
        else:
            instance = session.query(cls).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            session.add(instance)
            session.flush()
            return instance

    @classmethod
    def update_or_create(cls, session, **kwargs):
        """Update an existing record or create a new one."""
        pass

    @classmethod
    def get_or_create_many(cls, session, fkey=[], items=[]):
        """Get or create multiple records."""
        instances = [cls.get_or_create(session, fkey, **item) for item in items]
        return instances
    
    @classmethod
    def update_or_create_many(cls, session, items):
        """Update or create multiple records."""
        pass


engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


def init_db() -> None:
    """Create database tables from SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield a database session and ensure it is closed."""
    with Session() as db:
        yield db

DBSessionDep = Annotated[Session, Depends(get_session)]