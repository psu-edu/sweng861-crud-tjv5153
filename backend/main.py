# Entry point for SWENG 861 CRUD project
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx
from okta_jwt.jwt import validate_token
from okta_jwt_verifier import BaseJWTVerifier
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


def verifyStatePostAuth(state: str):
    return state == "login"


def exchangeCodeForTokens(code: str):
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
    id_token = token_data.get("id_token")

    return access_token, id_token


# def validateAccessToken(token: str):
#     valid = validate_token(
#         token,
#         OKTA_URL,
#         "api://default",
#         OKTA_CLIENT_ID
#         )
 
#     #print("Validation result:", valid)
#     return valid is not None

async def validateTokens(token: str, token_type: str):
    jwt_verifier = BaseJWTVerifier(OKTA_URL, OKTA_CLIENT_ID, audience="api://default")

    try:
        if token_type == "id_token":
            await jwt_verifier.verify_id_token(token)
        elif token_type == "access_token":
            await jwt_verifier.verify_access_token(token)
        return True

    except Exception as e:
        print("Token validation failed:", str(e))
        return False
    
def getUserInfo(token: str):
    userinfo_response = httpx.get(f"{OKTA_URL}/v1/userinfo",
                                headers={"Authorization": f"Bearer {token}"})

    if userinfo_response.status_code != 200:
        print("Failed to fetch user info")
    else:
        userinfo = userinfo_response.json()
        print(userinfo["sub"])


@app.get("/authorization-code/callback/")
async def authCallback(code:str, state:str):

    if(verifyStatePostAuth(state)):
        #print("State verified")
        access_token, id_token = exchangeCodeForTokens(code)
  
        if(await validateTokens(access_token, "access_token") and await validateTokens(id_token, "id_token")):
            #print("Tokens validated")
            getUserInfo(access_token)
        else:
            print("Token validation failed")
            return {"status": "error", "message": "Token validation failed"}
    else:
        print("State verification failed")
        return {"status": "error", "message": "State verification failed"}


    return {"status": "authenticated"}


@app.get("/signin")
async def signin():
    redirect_uri = f"{authorization_url}?client_id={OKTA_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={BACKEND_URL}/authorization-code/callback&state=login"
    return RedirectResponse(url=redirect_uri)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")
