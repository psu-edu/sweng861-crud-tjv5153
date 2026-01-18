# Entry point for SWENG 861 CRUD project
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/hello")
def read_hello():
    return {"message": "Hello, World!"}