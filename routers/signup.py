# routers/signUp.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo import MongoClient
# from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
import hashlib

router = APIRouter()

# Replace with your actual MongoDB URI and collection name
client = MongoClient("mongodb://localhost:27017/")
db = client["webterminal"]
COLLECTION_NAME = "login_users"

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")


# router to go to signUp page
@router.get("/signUp/")
def postAdd(request:Request):
    return templates.TemplateResponse("signup.html",{"request":request})

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/signupform/", response_class=HTMLResponse)
async def signup(request: Request,
                 firstName: str = Form(...),
                 lastName: str = Form(...),
                 email: str = Form(...),
                 userName: str = Form(...),
                 password: str = Form(...),
                 confirmPassword: str = Form(...)):

    if password != confirmPassword:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Passwords do not match"})

    user = db[COLLECTION_NAME].find_one({"username": userName})
    if user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
    
    hashed_password = get_password_hash(password)
    db[COLLECTION_NAME].insert_one({
        "first_name": firstName,
        "last_name": lastName,
        "email": email,
        "username": userName,
        "hashed_password": hashed_password
    })
    
    return RedirectResponse(url="/", status_code=303)
