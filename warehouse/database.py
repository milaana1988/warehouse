from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = "sqlite:///./warehouse.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.

    This context manager handles the creation and teardown of a database 
    session. It ensures that if any exception occurs within the block, 
    the transaction is rolled back. Otherwise, it commits the transaction.

    Yields:
        session: A SQLAlchemy ORM session.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit the transaction if no exceptions occur
    except:
        session.rollback()  # Rollback the transaction on exception
        raise
    finally:
        session.close()  # Close the session after operations
