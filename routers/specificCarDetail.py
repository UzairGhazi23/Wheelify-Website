from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from bson import ObjectId
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["webterminal"]

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Helper function to convert ObjectId to string
def convert_objectid(car):
    car['_id'] = str(car['_id'])
    return car


@router.get("/carDetails/{car_id}", response_class=HTMLResponse)
async def car_details(car_id: str, request: Request):
    try:
        car = db['feature_cars'].find_one({"_id": ObjectId(car_id)})
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        car = convert_objectid(car)
        return templates.TemplateResponse("displayspecificcar.html", {"request": request, "car": car})
    except Exception as e:
        logger.error("Error: %s", e)  # Log any errors encountered
        raise HTTPException(status_code=500, detail=str(e))  # Return the error message
