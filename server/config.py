import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

DB_MODE = os.environ.get('UPLOAD_FOLDER', 'offline')
if 'online' == DB_MODE:
    uri = os.environ.get('DB_CONN')
else:
    uri = 'mongodb://localhost:27017'
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.qltcxn
