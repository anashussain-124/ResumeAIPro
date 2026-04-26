from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.mongodb_uri)
db = client.get_default_database()
resumes_collection = db.resumes
orders_collection = db.orders

def get_db():
    return db

def init_indexes():
    resumes_collection.create_index("resume_id", unique=True)
    resumes_collection.create_index("email")
    resumes_collection.create_index("status")
    orders_collection.create_index("order_id", unique=True)
    orders_collection.create_index("resume_id")