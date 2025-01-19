from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Response
from motor.motor_asyncio import AsyncIOMotorClient
from itsdangerous import URLSafeSerializer
import hashlib

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# MongoDB connection
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.webterminal
login_users = db.login_users

# Session serializer
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
serializer = URLSafeSerializer(SECRET_KEY)

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

@router.get("/signin/", response_class=HTMLResponse)
async def get_signin_form(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@router.post("/signinform/")
async def signin(response: Response, request: Request, userName: str = Form(...), password: str = Form(...)):
    user = await login_users.find_one({"username": userName})
    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse("signin.html", {"request": request, "error": "Invalid credentials"})
    
    session_data = {"user_id": str(user["_id"])}
    session_cookie = serializer.dumps(session_data)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("session", session_cookie)
    return response

@router.get("/logout/")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response
