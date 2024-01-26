"""models for postcard applicaiton"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    def serialize(self):
        """return json serializable dict of data"""

        return{
            "id": self.id,
            "image_url": self.image_url,
            "created_at": self.created_at,
        }

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)