from fastapi import FastAPI
from .database import engine, Base
from .routers import todos, auth

# Create database tables (this will also create the users table)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API with JWT",
    description="Secure Todo API with user authentication",
    version="2.0.0"
)

app.include_router(todos.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Todo API. Go to /docs for interactive documentation."}