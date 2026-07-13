from fastapi import FastAPI
from .database import engine, Base
from routes.auth_routes import router as auth_router
from middleware.logging_middleware import log_requests

app = FastAPI(title="Auth System API", version="1.0.0")

# Create database tables
Base.metadata.create_all(bind=engine)

# Add middleware
app.middleware("http")(log_requests)

# Include routers
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Auth System API is running"}