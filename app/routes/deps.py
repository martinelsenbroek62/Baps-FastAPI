from app.database.database import SessionLocal
from app.database.database import engine

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # pylint: disable=no-member


def get_engine():
    return engine
