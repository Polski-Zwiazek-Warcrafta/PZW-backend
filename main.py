from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os 
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["PZW"] # data base name
users_collection = db["users"] # collection of users 

# JWT Configuration
load_dotenv()  # Load environment variables from .env file
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    # Check if the user already exists
    if users_collection.find_one({"username": data['username']}):
        return jsonify({"message": "User already exists"}), 400

    # Hash the user's password
    hashed_password = generate_password_hash(data['password'], method='sha256')
     
    # Insert new user into the MongoDB collection
    users_collection.insert_one({"username": data['username'], "password_hash": hashed_password})
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # Find the user in the database
    user = users_collection.find_one({"username": data['username']})

    if user and check_password_hash(user['password_hash'], data['password']):
        # Create JWT token
        access_token = create_access_token(identity=user['username'])
        return jsonify(access_token=access_token)

    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(debug=True)