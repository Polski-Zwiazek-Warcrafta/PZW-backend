from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import auth_bp 

@auth_bp.route('/register', methods=['POST'])
def register():
    db = current_app.config["db"]
    users_collection = db["users"]
    
    data = request.json
    if users_collection.find_one({"username": data['username']}):
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    user_data = {
        "username": data['username'],
        "password_hash": hashed_password,
        "isAdmin": data.get("isAdmin", False),  
        "createdAt": datetime.utcnow(),
        "updatedAt": None,
        "deletedAt": None 
    }

    users_collection.insert_one(user_data)
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    db = current_app.config["db"]
    users_collection = db["users"]

    data = request.json
    user = users_collection.find_one(
        {"username": data['username'], "deletedAt": None} 
    )

    if user and check_password_hash(user['password_hash'], data['password']):
        access_token = create_access_token(identity=user['username'])
        return jsonify(access_token=access_token)

    return jsonify({"message": "Invalid credentials or user deleted"}), 401