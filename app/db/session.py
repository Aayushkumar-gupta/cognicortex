from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Get database URL from environment or config
DATABASE_URL = settings.DATABASE_URL

# 2. Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# 3. Create SessionLocal — the session we will use in routes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for all SQLAlchemy models
Base = declarative_base()

# 5. Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
