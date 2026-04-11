import logging
from sqlmodel import SQLModel, Session, create_engine
from app.config import get_settings
from contextlib import contextmanager

logger = logging.getLogger(__name__)

db_uri = get_settings().database_uri

# SQLite doesn't support connection pooling args
if db_uri.startswith("sqlite"):
    engine = create_engine(
        db_uri,
        echo=get_settings().env.lower() in ["dev", "development", "test", "testing", "staging"],
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        db_uri, 
        echo=get_settings().env.lower() in ["dev", "development", "test", "testing", "staging"],
        pool_size=get_settings().db_pool_size,
        max_overflow=get_settings().db_additional_overflow,
        pool_timeout=get_settings().db_pool_timeout,
        pool_recycle=get_settings().db_pool_recycle,
    )

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all():
    SQLModel.metadata.drop_all(bind=engine)
    
def _session_generator():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

def get_session():
    yield from _session_generator()

@contextmanager
def get_cli_session():
    yield from _session_generator()