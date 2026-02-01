# Entry point for SWENG 861 CRUD project
from datetime import datetime
from urllib import request
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
import httpx
import jwt
from okta_jwt.jwt import validate_token
from okta_jwt_verifier import BaseJWTVerifier
import os
import sqlite3
import thirdPartyApi
import restapi_helpers


load_dotenv()
OKTA_URL = os.getenv("OKTA_URL")
OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID")
OKTA_CLIENT_SECRET = os.getenv("OKTA_CLIENT_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL")
DB_PATH = os.getenv("DB")

try:
    conn = sqlite3.connect(DB_PATH)
    print("Users Database connection successful")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT,
        email TEXT,
        lastAccessTime INTEGER,
        createdTime INTEGER
    )''')
    conn.commit()
except sqlite3.Error as e:
    print(f"Users Database connection failed: {e}")

app = FastAPI()

templates = Jinja2Templates(directory="../frontend/templates")

# Fetch OpenID Connect metadata
metadata = httpx.get(f"{OKTA_URL}/.well-known/openid-configuration").json()
authorization_url = metadata["authorization_endpoint"]
token_url = metadata["token_endpoint"]


#create (POST)
@app.post("/cars/", response_model=restapi_helpers.Car)
async def add_car(car: restapi_helpers.Car):
    if not restapi_helpers.add_car_to_db(car):
        return JSONResponse(status_code=500, content={"error": "Failed to add car"})
    else:
        return JSONResponse(status_code=200, content={"message": "Car added successfully"})

#read (GET)
@app.get("/cars/{vin}", response_model=restapi_helpers.Car)
async def get_car(vin: str):
    car = restapi_helpers.get_car_from_db(vin)
    if car:
        return car
    else:
        return JSONResponse(status_code=404, content={"error": "Car not found"})

#update price only (PUT)
@app.put("/cars/{vin}/{price}")
async def update_car_price(vin: str, price: float):
    if not restapi_helpers.update_price_in_db(vin, price):
        return JSONResponse(status_code=404, content={"error": "Car not found"})
    else:
        return JSONResponse(status_code=200, content={"message": "Car price updated successfully"})

#update (PUT)
@app.put("/cars/{vin}", response_model=restapi_helpers.Car)
async def update_car(vin: str, car: restapi_helpers.Car):
    if not restapi_helpers.update_car_in_db(vin, car):
        return JSONResponse(status_code=404, content={"error": "Car not found"})
    else:
        return JSONResponse(status_code=200, content={"message": "Car updated successfully"})
    
#delete
@app.delete("/cars/{vin}")
async def sold_car(vin: str):
    if not restapi_helpers.delete_car_from_db(vin):
        return JSONResponse(status_code=404, content={"error": "Car not found"})
    else:
        return JSONResponse(status_code=200, content={"message": "Car sold successfully"})


@app.get("/health")
async def read_health():
    return {"status": "ok"}


async def isAuthenticated(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return False
    else:
        is_valid = await validateTokens(session_id, "access_token")
        print("Verified using depends")
        return is_valid

@app.get("/api/hello")
async def protected_hello(request: Request, verified: bool = Depends(isAuthenticated)):
    return {"message": f"Hello, {request.state.user}. Email: {request.state.email}. This is the protected hello api endpoint."}


@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    if request.url.path != "/api/hello":
        response = await call_next(request)
        #print("No authentication required for this path")
        return response

    session_id = request.cookies.get("session_id")
    #print(f"Session ID: {session_id}")
    if not session_id:
        print("unauthorized1")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"Unauthorized": "Valid access token is required"}
        )
    else:
        is_valid = await validateTokens(session_id, "access_token")
        if not is_valid:
            print("unauthorized2")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"Unauthorized": "Invalid session Id"}
            )
        else:
            print("Session ID is valid")
            user_info = extractUserInfo(session_id)
            print(f"User Info from Middleware: {user_info}")

            #Attach user info to the request object for downstream use
            request.state.user = user_info['name']
            request.state.email = user_info['email']

            response = await call_next(request)
            return response

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

    if token_response.status_code != 200:
        print("Failed to exchange code for tokens")
        return None, None
    else:
        token_data = token_response.json()

        access_token = token_data.get("access_token")
        id_token = token_data.get("id_token")


        return access_token, id_token

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
    
def extractUserInfo(token: str):
    
    decoded_token = jwt.decode(token, options={"verify_signature": False})
    userinfo = {}
    #print(f"Decoded Token: {decoded_token}")
    userinfo['name'] = f'{decoded_token.get('name')} {decoded_token.get('lastName')}'
    userinfo['email'] = decoded_token.get('email')  
    userinfo['auth_time'] = decoded_token.get('auth_time')
    userinfo['iat'] = decoded_token.get('iat')
    userinfo['uid'] = decoded_token.get('uid')
    print(userinfo)

    return userinfo

def addUsertoDB(userinfo):
    User(id=userinfo['uid'], username=userinfo['name'], email=userinfo['email'], accessTime=userinfo['auth_time'])

@app.get("/authorization-code/callback/")
async def authCallback(response: HTMLResponse, code:str, state:str):

    if(verifyStatePostAuth(state)):
        #print("State verified")
        access_token, id_token = exchangeCodeForTokens(code)
  
        if(await validateTokens(access_token, "access_token") and await validateTokens(id_token, "id_token")):
            #print("Tokens validated")
            user_info = extractUserInfo(access_token)
            addUsertoDB(user_info)
        else:
            print("Token validation failed")
            return {"status": "error", "message": "Token validation failed"}
    else:
        print("State verification failed")
        return {"status": "error", "message": "State verification failed"}

    response.set_cookie(
            key="session_id",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600
        )

    return {"status": "authenticated"}


@app.get("/signin")
async def signin():
    redirect_uri = f"{authorization_url}?client_id={OKTA_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={BACKEND_URL}/authorization-code/callback&state=login"
    return RedirectResponse(url=redirect_uri)

@app.get("/catFacts")
async def cat_facts():
    #this just gets one cat fact from the API and stores it in the database
    stat = thirdPartyApi.fetch_cat_facts_from_api(1)
    if stat:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "Cat Facts API data stored successfully"})
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "Failed to store Cat Facts API data"})

@app.get("/catFacts/{numFacts}")
async def cat_facts(numFacts: int):
    #this just gets one cat fact from the API and stores it in the database
    stat = thirdPartyApi.fetch_cat_facts_from_api(numFacts)
    if stat:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": f"Cat Facts API data stored successfully for {numFacts} facts"})
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "Failed to store Cat Facts API data"})

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


class User():
    def __init__(self, id, username, email, accessTime):
        self.id = id
        self.username = username
        self.email = email
        self.lastAccessTime = accessTime

        cursor = conn.cursor()
        #If user does not exist insert new record else ignore
        cursor.execute("INSERT OR IGNORE INTO users (id, username, email, lastAccessTime, createdTime) VALUES (?, ?, ?, ?, ?)", 
                       (self.id, self.username, self.email, self.lastAccessTime, self.lastAccessTime))
        conn.commit()

        cursor = conn.cursor()
        #update last access time on each login
        cursor.execute("UPDATE users SET lastAccessTime = ? WHERE id = ?", (self.lastAccessTime, self.id))
        conn.commit()