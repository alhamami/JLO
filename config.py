import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://fmzbxccjemottn:87bde68550a3d51f5a7a215ecd607c44e8792a8e5ec842d7011a59a2a5408653@ec2-52-0-93-3.compute-1.amazonaws.com:5432/d3sc7ooguj4bjf'
# Remove console warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
