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
token_url = metadata["token_endpoint"]

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/api/hello")
def read_hello():
    return {"message": "Hello, World!"}

@app.get("/authorization-code/callback")
async def authCallback(code:str):
    token_response = httpx.post(token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{BACKEND_URL}/authorization-code/callback",
                "client_id": OKTA_CLIENT_ID,
                "client_secret": OKTA_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"})

    token_data = token_response.json()

    access_token = token_data.get("access_token")

    userinfo_response = httpx.get(f"{OKTA_URL}/v1/userinfo",
                                  headers={"Authorization": f"Bearer {access_token}"})

    if userinfo_response.status_code != 200:
        print("Failed to fetch user info")
    else:
        userinfo = userinfo_response.json()
        print(userinfo)

    return {"status": "authenticated"}

@app.get("/signin")
async def signin():
    redirect_uri = f"{authorization_url}?client_id={OKTA_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={BACKEND_URL}/authorization-code/callback&state=none"
    return RedirectResponse(url=redirect_uri)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")
