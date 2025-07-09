import os
from dotenv import load_dotenv

load_dotenv()  

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/uber_clone')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
