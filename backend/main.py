# Entry point for SWENG 861 CRUD project
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="../frontend/templates")

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/hello")
def read_hello():
    return {"message": "Hello, World!"}

@app.get("/", include_in_schema=False)
@app.get("/posts", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")