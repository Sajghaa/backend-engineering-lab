from fastapi import FastAPI
from app.api.v1.router import router as v1_router

app = FastAPI(
    title="Item Catalog API",
    description="A simple API to manage items",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Item Catalog API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}