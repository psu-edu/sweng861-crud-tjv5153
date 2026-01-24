# Entry point for SWENG 861 CRUD project
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
import os

load_dotenv()
OKTA_URL = os.getenv("OKTA_URL")
OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()

templates = Jinja2Templates(directory="../frontend/templates")

# Fetch OpenID Connect metadata
metadata = httpx.get(f"{OKTA_URL}/.well-known/openid-configuration").json()
authorization_url = metadata["authorization_endpoint"]

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/hello")
def read_hello():
    return {"message": "Hello, World!"}

@app.get("/authorization-code/callback")
def authCallback(code:str):
    return {"status": "authenticated"}

@app.get("/signin")
async def signin():
    redirect_uri = f"{authorization_url}?client_id={OKTA_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={BACKEND_URL}/authorization-code/callback&state=none"
    return RedirectResponse(url=redirect_uri)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")
