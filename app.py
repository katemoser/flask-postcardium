"""Application for uploading postcards"""

import os
from dotenv import load_dotenv

from flask import Flask, jsonify, request
# from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS

from uuid import uuid4 as uuid

import boto3

from models import (
    db,
    connect_db,
    Photo,
    Postcard
)

load_dotenv()

BUCKET_NAME = os.environ["BUCKET_NAME"]

app = Flask(__name__)
CORS(app)

# Configure app and db

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# toolbar = DebugToolbarExtension(app)
s3 = boto3.client("s3")

connect_db(app)


################# PHOTOS #################

@app.get("/api/photos")
def get_all_photos():
    """
    Get info on all photos. Returns JSON like:

    {
        "photos": [
            {
                "created_at": "Fri, 26 Jan 2024 02:57:30 GMT",
                "id": 1,
                "image_url": "01ea49fa-b20e-462d-b5b5-e8b084f8ae5c"
            }, {}...
        ]
    }
    """

    photos = Photo.query.all()

    serialized = [p.serialize() for p in photos]

    return jsonify(photos=serialized)


@app.post("/api/photos/exif")
def store_locally_get_gps_data():
    """save file locally and get exif data to return"""

    file_obj = request.files['photo']
    file_name = str(uuid())

    file_obj.filename = file_name
    # save to disk with new uuid as name
    file_obj.save(file_obj.filename)
    # print("file obj after save:", file_obj)
    # # TODO: find a way to save this in a temporary file
    # # https://docs.python.org/3/library/tempfile.html

    location_data = Photo.get_location_from_file(file_obj.filename)
    # print("city, state, country", city, state, country)
    # add file name to dict for reference
    location_data["file_name"] = file_name
    # breakpoint()
    return jsonify(location_data)


@app.post("/api/photos")
def upload_photo():
    """
    Upload a locally stored file and create photo resource. Returns JSON like:

    {
        "photo": {
            "created_at": "Fri, 26 Jan 2024 02:57:30 GMT",
            "id": 1,
            "image_url": "01ea49fa-b20e-462d-b5b5-e8b084f8ae5c"
        }
    }
    """
    print("IN UPLOAD PHOTO request:", request)

    file_name = request.json.get("file_name")
    city = request.json.get("city")
    state = request.json.get("state")
    country = request.json.get("country")
    latitude = request.json.get("latitude")
    longitude = request.json.get("longitude")

    if(not latitude or not longitude):
        address = {
            "city": city,
            "state": state,
            "country": country
        }
        location = Photo.get_lat_long_from_address(address)
        latitude = location[0]
        longitude = location[1]

    # TODO: refactor to model!
    response = s3.upload_file(
        file_name,
        BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType":"image/png"
        }
    )

    image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"

    photo = Photo(
        image_url=image_url,
        city=city,
        state=state,
        country=country,
        latitude=latitude,
        longitude=longitude
    )

    print("response:", response, "photo:", photo)

    db.session.add(photo)
    db.session.commit()

    return jsonify(photo=photo.serialize())

@app.get("/api/photos/<int:photo_id>")
def get_photo(photo_id):
    """
    Get info on one photo. Returns JSON like:

    {
        "photo": {
            "created_at": "Fri, 26 Jan 2024 02:57:30 GMT",
            "id": 1,
            "image_url": "01ea49fa-b20e-462d-b5b5-e8b084f8ae5c"
        }
    }
    """

    photo = Photo.query.get_or_404(photo_id)
    # TODO: More graceful handling of 404 -- make sure I'm sending back a JSON response.
    return jsonify(photo=photo.serialize())




################# POSTCARDS #################


@app.get("/api/postcards")
def get_all_postcards():
    """ get info on all postcards"""

    postcards = Postcard.query.all()

    serialized = [p.serialize() for p in postcards]

    return jsonify(postcards=serialized)

@app.post("/api/postcards")
def create_postcard():
    """Create a postcard

    send json like:

    {
        title, message, photo_id
    }
    """

    # TODO: Add sceme validation

    message = request.json.get("message")
    photo_id = int(request.json.get("photoId"))

    # TODO: deal with location!

    postcard = Postcard(
        message=message,
        photo_id=photo_id
    )

    db.session.add(postcard)
    db.session.commit()
    return jsonify(postcard = postcard.serialize())


@app.get("/api/postcards/<int:postcard_id>")
def get_postcard(postcard_id):
    """TODO: fix this docstring"""

    postcard= Postcard.query.get_or_404(postcard_id)

    return jsonify(postcard=postcard.serialize())
