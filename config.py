import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://abskbousjroxwx:9b24f629e579f4dd9a33d26eadb6d7de70fa5237a80a63d673bca76fe732dac6@ec2-54-145-188-92.compute-1.amazonaws.com:5432/d3oaclh4elpp9b'
# Remove console warning
SQLALCHEMY_TRACK_MODIFICATIONS = False