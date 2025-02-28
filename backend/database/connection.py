# backend/database/connection.py
from pymongo import MongoClient
from backend.config.settings import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.DATABASE_NAME]

def get_user_collection():
    return db.users
