"""models for postcard applicaiton"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Photo(db.Model):
    """class with metadata about a photo"""
    __tablename__ = "photos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
