from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,Response
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from pydantic import BaseModel
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

 
# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['webterminal']
fs = GridFS(db)

# # Define Pydantic model for car form data
# class CarForm(BaseModel):
#     car_name: str
#     car_price: int
#     city: str
#     category: str
#     description: str
#     registered: str



# Route to upload car data
@router.post("/addCarForm/", response_class=HTMLResponse)
async def upload_car(request: Request, car_name: str = Form(...), car_price: int = Form(...), city: str = Form(...), description: str = Form(...), category: str = Form(...), registered: str = Form(...), file: UploadFile = File(...)):
    # print("raees zakir adsffds")
    try:
        contents = await file.read()
        picture_id = fs.put(contents, filename=file.filename)

        car_document = {
            "car_name": car_name,
            "car_price": car_price,
            "city": city,
            "registered": registered,
            "category":category,
            "description": description,
            "picture_id": picture_id
        }

        db['feature_cars'].insert_one(car_document)
        logger.info(f"Car uploaded successfully: {car_name}, {car_price}, {category}")

        return RedirectResponse(url="/displayallcars", status_code=303)

    except Exception as e:
        logger.error(f"Error uploading car: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



# router to get the last added car by user
@router.get("/image/{picture_id}", response_class=Response)
async def get_image(picture_id: str):
    try:
        grid_out = fs.get(ObjectId(picture_id))
        return Response(content=grid_out.read(), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=404, detail="Image not found")

# router for deletion of the car
@router.post("/deleteCar/{car_id}")
async def delete_car(car_id: str):
    try:
        car = db['feature_cars'].find_one({"_id": ObjectId(car_id)})
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        # Delete the picture from GridFS
        fs.delete(ObjectId(car["picture_id"]))

        # Delete the car document from the database
        db['feature_cars'].delete_one({"_id": ObjectId(car_id)})

        logger.info(f"Car deleted successfully: {car_id}")
        return RedirectResponse(url="/displayallcars", status_code=303)

    except Exception as e:
        logger.error(f"Error deleting car: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/updateCar/{car_id}", response_class=HTMLResponse)
async def update_car(car_id: str, car_name: str = Form(...), car_price: int = Form(...), category: str = Form(...), city: str = Form(...), description: str = Form(...), registered: str = Form(...), file: UploadFile = File(None)):
    try:
        update_fields = {
            "car_name": car_name,
            "car_price": car_price,
            "city": city,
            "category":category,
            "description": description,
            "registered": registered,
        }

        if file:
            contents = await file.read()
            picture_id = fs.put(contents, filename=file.filename)
            update_fields["picture_id"] = picture_id

            # Retrieve the old car document to delete the old picture
            car = db['feature_cars'].find_one({"_id": ObjectId(car_id)})
            if car and "picture_id" in car:
                fs.delete(ObjectId(car["picture_id"]))

        db['feature_cars'].update_one({"_id": ObjectId(car_id)}, {"$set": update_fields})
        logger.info(f"Car updated successfully: {car_id}")
        print("error is here")
        print("hahhahhahahha")
        return RedirectResponse(url="/displayallcars", status_code=303)

    except Exception as e:
        logger.error(f"Error updating car: {e}")
        raise HTTPException(status_code=500, detail="msla haiiiii")


# to display all cars
@router.get("/displayallcars", response_class=HTMLResponse)
async def display_all_cars(request: Request):
    cars = list(db['feature_cars'].find())
    return templates.TemplateResponse("displayallcars.html", {"request": request, "cars": cars})