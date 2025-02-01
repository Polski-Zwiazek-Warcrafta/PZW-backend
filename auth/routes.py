from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import auth_bp 
import re

@auth_bp.route('/register', methods=['POST'])
def register():
    db = current_app.config["db"]
    users_collection = db["users"]
    
    data = request.json
    
    if not all(key in data and data[key] for key in ['password', 'repeatPassword', 'username']):
        return jsonify({"error": "error.missingFields"}), 400
    
    if data['password'] != data['repeatPassword']:
        return jsonify({"error": "error.passwordsNotMatch"}), 400

    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    if not re.match(password_pattern, data['password']):
        return jsonify({"error": "error.invalidPassword"}), 400
    
    if users_collection.find_one({"username": data['username']}):
        return jsonify({"error": "error.userExists"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    user_data = {
        "username": data['username'],
        "password_hash": hashed_password,
        "isAdmin": data.get("isAdmin", False),  
        "createdAt": datetime.utcnow(),
    }

    users_collection.insert_one(user_data)
    
    return jsonify({"message": "success.userCreated", "success": True}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    db = current_app.config["db"]
    users_collection = db["users"]

    data = request.json
    
    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "error.missing.fields"}), 400
    
    user = users_collection.find_one(
        {"username": data['username'], "deletedAt": None} 
    )

    if user and check_password_hash(user['password_hash'], data['password']):
        access_token = create_access_token(identity=user['username'])
        return jsonify({"access_token": access_token, "success": True})

    return jsonify({"error": "error.invalid.credentials"}), 401