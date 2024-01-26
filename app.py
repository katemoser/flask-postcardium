"""Application for uploading postcards"""

# import os

from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/api/photos")
def get_all_photos():
    """get info on all photos"""

    return jsonify("These are all the photos")


@app.get("/api/postcards")
def get_all_postcards():
    """ get info on all postcards"""

    return jsonify("these are all the postcards")
