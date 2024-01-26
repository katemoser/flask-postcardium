"""Application for uploading postcards"""

import os
from dotenv import load_dotenv

from flask import Flask, jsonify, request
# from flask_debugtoolbar import DebugToolbarExtension

from uuid import uuid4 as uuid

import boto3

from models import (
    db,
    connect_db,
    Photo
)

load_dotenv()

BUCKET_NAME = os.environ["BUCKET_NAME"]

app = Flask(__name__)

# Configure app and db

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# toolbar = DebugToolbarExtension(app)
s3 = boto3.client("s3")

connect_db(app)


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


@app.post("/api/photos")
def upload_photo():
    """
    Upload a fileobj to s3 and create photo resource. Returns JSON like:

    {
        "photo": {
            "created_at": "Fri, 26 Jan 2024 02:57:30 GMT",
            "id": 1,
            "image_url": "01ea49fa-b20e-462d-b5b5-e8b084f8ae5c"
        }
    }
    """

    file_obj = request.files['photo']
    file_name = str(uuid())

    response = s3.upload_fileobj(
        file_obj,
        BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType":"image/png"
        }
    )

    photo = Photo(
        image_url=file_name
    )

    print("response:", response, "photo:", photo)

    db.session.add(photo)
    db.session.commit()

    return jsonify(photo.serialize())

@app.get("/api/photos/<int:id>")
def get_photo(id):
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

    photo = Photo.query.get_or_404(id)
    # TODO: More graceful handling of 404 -- make sure I'm sending back a JSON response.
    return jsonify(photo=photo.serialize())


@app.get("/api/postcards")
def get_all_postcards():
    """ get info on all postcards"""

    return jsonify("these are all the postcards")
