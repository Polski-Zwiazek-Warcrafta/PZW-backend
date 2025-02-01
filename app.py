from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus

from auth.routes import auth_bp
from auth.schema import user_schema

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = quote_plus(os.getenv("DB_PASS"))
DB_HOST = os.getenv("DB_HOST")

MONGO_URI = f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    app.config["db"] = db

    if "users" not in db.list_collection_names():
        db.create_collection("users", validator=user_schema)
    print("✅ Successfully connected to the MongoDB database!")

except:
    print("❌ Failed to connect to MongoDB:")

if "users" not in db.list_collection_names():
    db.create_collection("users", validator=user_schema)

app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)