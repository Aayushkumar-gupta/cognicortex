from fastapi import FastAPI
from app.api.v1.routes.health import router as health_router

app = FastAPI(title="CogniCortex")

# Include routes
app.include_router(health_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}