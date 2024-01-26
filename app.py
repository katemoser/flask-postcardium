"""Application for uploading postcards"""

import os

from flask import Flask, jsonify, request
import boto3

app = Flask(__name__)

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]

@app.get("/api/photos")
def get_all_photos():
    """get info on all photos"""

    return jsonify("These are all the photos")


@app.post("/api/photos")
def upload_photo():
    """upload a fileobj to s3 and create photo resource"""

    new_photo = request.files['photo']
    file_name = new_photo.filename

    response = s3.upload_fileobj(
        new_photo,
        BUCKET_NAME,
        file_name,
        ExtraArgs={
            "ContentType":"image/png"
        }
    )

    print("response:", response)

    return jsonify({"response": "uploaded"})


@app.get("/api/postcards")
def get_all_postcards():
    """ get info on all postcards"""

    return jsonify("these are all the postcards")
