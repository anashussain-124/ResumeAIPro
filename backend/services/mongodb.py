from pymongo import MongoClient
from settings import settings

client = MongoClient(
    settings.mongodb_uri,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=15000,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True
)
db = client.resume_builder
resumes_collection = db.resumes
users_collection = db.users

def get_db():
    return db