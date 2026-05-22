from fastapi import FastAPI
from .database import engine, Base
from .routers import todos

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="Simple CRUD Todo API built with FastAPI",
    version="1.0.0"
)

app.include_router(todos.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Todo API. Go to /docs for interactive documentation."}