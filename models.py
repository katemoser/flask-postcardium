"""models for postcard applicaiton"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# from PIL import Image
# from PIL.ExifTags import TAGS, GPSTAGS

from GPSPhoto import gpsphoto
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="postcardium")

db = SQLAlchemy()

class Photo(db.Model):
    """class with metadata about a photo"""
    __tablename__ = "photos"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    image_url = db.Column(
        db.String(500),
        nullable=False,
    )

    city = db.Column(
        db.String(100)
    )

    state = db.Column(
        db.String(100)
    )

    country = db.Column(
        db.String(100)
    )
    # latitude = db.Column(
    #     db.String(50),
    # )

    # longitude = db.Column(
    #     db.String(50),
    # )

    # location = db.Column(
    #     db.String(100),
    # )

    # TODO: where should I put my alt text -- photo or postcard?

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    # postcards = relationship to postcards table

    @classmethod
    def get_location(cls, file_path):
        """get location data off file returns tuple of (city, state, country)"""

        data = gpsphoto.getGPSData(file_path)
        print("DATA:", data)
        latitude = data.get("Latitude")
        longitude = data.get("Longitude")

        # TODO: if there is no lat/long, don't try and look up a location
        if not latitude or not longitude:
            city = None
            state = None
            country = None
        else:
            location = geolocator.reverse(f"{latitude},{longitude}")
            address = location.raw['address']
            print("address:", address)
            city = address.get("city")
            state = address.get("state")
            country = address.get("country")
        return (city, state, country)


    def serialize(self):
        """return json serializable dict of data"""

        return{
            "id": self.id,
            "image_url": self.image_url,
            "created_at": self.created_at,
            "city": self.city,
            "state": self.state,
            "country": self.country
        }


class Postcard(db.Model):
    """Geolocated Photo and message, anonymously posted"""

    __tablename__ = "postcards"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    message = db.Column(
        db.String(300),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    photo_id = db.Column(
        db.Integer,
        db.ForeignKey("photos.id"),
        nullable=False,
    )

    photo = db.relationship("Photo", backref="postcard")

    # add prop func to make location
    def serialize(self):
        photo_url = self.photo.image_url
        location = self.photo.city
        return {
            "id": self.id,
            "message": self.message,
            "location": location,
            "created_at": self.created_at,
            "photo_id": self.photo_id,
            "photo_url": photo_url,
        }


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
