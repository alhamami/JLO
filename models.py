import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
from flask_migrate import Migrate


database_path = 'postgres://abskbousjroxwx:9b24f629e579f4dd9a33d26eadb6d7de70fa5237a80a63d673bca76fe732dac6@ec2-54-145-188-92.compute-1.amazonaws.com:5432/d3oaclh4elpp9b'

db = SQLAlchemy()
def get_DB():
    return db
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(150))
    facebook_link = db.Column(db.String(150))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(150))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(150))
    Show = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(150))
    facebook_link = db.Column(db.String(150))
    website_link = db.Column(db.String(150))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(150))
    Show = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
