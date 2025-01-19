
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.staticfiles import StaticFiles
from itsdangerous import URLSafeTimedSerializer
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from gridfs import GridFS
from fastapi_login import LoginManager
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from gridfs import GridFS
from starlette.middleware.sessions import SessionMiddleware
from bson import ObjectId
import logging

app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="templates")
SECRET = "mysecretkey"
serializer = URLSafeTimedSerializer(SECRET)



# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# MongoDB connection details
client = MongoClient('mongodb://localhost:27017')
db = client['webterminal']
fs = GridFS(db)

DATABASE_NAME = "webterminal"
COLLECTION_NAME = "login_users"

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
fs = GridFS(db)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Main route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    cars = list(db['feature_cars'].find())
    return templates.TemplateResponse("index.html", {"request": request, "cars": cars})

# storing images in the database
@app.get("/image/{picture_id}")
async def get_car_image(picture_id: str):
    try:
        image_data = fs.get(ObjectId(picture_id))
        if image_data is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_data.read(), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# router to go to postaddpage
@app.get("/postAddPage/")
def postAdd(request:Request):
    return templates.TemplateResponse("postadd.html",{"request":request})

# router to go to caradd page
@app.get("/addCarPage/",response_class=HTMLResponse)
def addCarPage(request:Request):
    return templates.TemplateResponse("addcar.html", {"request": request})


@app.get("/check_signin_status")
async def check_signin_status(request: Request):
    session = request.cookies.get("session")
    if session:
        return JSONResponse({"signed_in": True})
    else:
        return JSONResponse({"signed_in": False})


# Include the car router
from routers import carRouter
app.include_router(carRouter.router)
# Include the signup router
from routers import signup
app.include_router(signup.router)
# Include the buycarpage router
from routers import buyCarPage
app.include_router(buyCarPage.router)
# router for specific car detail
from routers import specificCarDetail
app.include_router(specificCarDetail.router)
# router for signin formm
from routers import signin
app.include_router(signin.router)