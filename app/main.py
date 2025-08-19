from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import health

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"service": settings.app_name, "env": settings.environment}
