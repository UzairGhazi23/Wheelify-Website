# routers/car_search.py
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from typing import Optional
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["webterminal"]

# Logger setup
logger = logging.getLogger(__name__)

# router to go to buycar page
@router.get("/buyCarPage/",response_class=HTMLResponse)
def buyCarPage(request:Request):
    cars = list(db['feature_cars'].find())
    return templates.TemplateResponse("buyCarPage.html",{"request":request, "cars":cars})



from fastapi import HTTPException

from fastapi import HTTPException

@router.get("/searchCars/", response_class=HTMLResponse)
async def search_cars(
    request: Request,
    carName: Optional[str] = Query(None),
    carPriceMin: Optional[int] = Query(None),
    carPriceMax: Optional[int] = Query(None),
    category: Optional[str] = Query(None)
):
    query = {}
    print(carPriceMax)
    if carName:
        query["car_name"] = {"$regex": carName, "$options": "i"}
    elif carPriceMax is None:
        return templates.TemplateResponse("buyCarPage.html",{"request":request, "error": "enter all details"})
    if carPriceMin is not None and carPriceMax is not None:
        query["car_price"] = {"$gte": carPriceMin, "$lte": carPriceMax}
    elif carPriceMin is not None:
        query["car_price"] = {"$gte": carPriceMin}
    elif carPriceMax is not None:
        query["car_price"] = {"$lte": carPriceMax}

    if category:
        query["category"] = category
    
    logger.info("Query: %s", query)  # Log the constructed query
    
    try:
        cars_cursor = db['feature_cars'].find(query)
        cars = list(cars_cursor)
        logger.info("Found cars: %s", cars)  # Log the found cars
        
        if not cars:
            logger.warning("No cars found matching the criteria")
            # raise HTTPException(status_code=404, detail="No cars found matching the criteria")
            return templates.TemplateResponse("buyCarPage.html",{"request":request, "error": "Invalid credentials"})
        
        return templates.TemplateResponse("buyCarPage.html", {"request": request, "cars": cars})
    except Exception as e:
        logger.error("Error: %s", e)  # Log any errors encountered
        raise HTTPException(status_code=500, detail=str(e))  # Return the error message