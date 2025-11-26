from fastapi import FastAPI
from app.api.v1.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME
)

# Include routes
app.include_router(health_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}