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
    def filter_by(cls, session, fkey=[], **kwargs):
        """Filter records based on provided keyword arguments."""
        if fkey:
            filters = {key: kwargs[key] for key in fkey if key in kwargs}
        else:
            filters = kwargs
        
        return session.query(cls).filter_by(**filters)
    
    @classmethod
    def get_or_create(cls, session, fkey=[], **kwargs):
        """Get an existing record or create a new one."""
        instance = cls.filter_by(session, fkey=fkey, **kwargs).all()
        
        if not instance:
            instance = cls(**kwargs)
            session.add(instance)
            session.flush()
        return instance

    @classmethod
    def update_or_create(cls, session, fkey=[], **kwargs):
        """Update an existing record or create a new one."""
        instance = cls.filter_by(session, fkey=fkey, **kwargs)
            
        if instance:
            instance.update(kwargs)
        else:
            instance = cls(**kwargs)
            session.add(instance)
        
        session.flush()
        

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