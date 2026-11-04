from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.user import router as user_router
from app.api.v1.routes.workflow_runs import router as workflow_runs_router
from app.api.v1.routes.workflows import router as workflow_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(health_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(workflow_runs_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")


@app.get("/")
def home():
    return {"message": "FastAPI is running!"}
