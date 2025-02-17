from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import auth_bp 
import re

@auth_bp.route('/register', methods=['POST'])
@jwt_required(optional=True)
def register():
    db = current_app.config["db"]
    users_collection = db["users"]
    
    data = request.json
    current_user = get_jwt_identity()
    
    if not all(key in data and data[key] for key in ['password', 'repeatPassword', 'username']):
        return jsonify({"error": "error.missingFields"}), 400
    
    if data['password'] != data['repeatPassword']:
        return jsonify({"error": "error.passwordsNotMatch"}), 400

    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    if not re.match(password_pattern, data['password']):
        return jsonify({"error": "error.invalidPassword"}), 400
    
    if users_collection.find_one({"username": data['username']}):
        return jsonify({"error": "error.userExists"}), 400
    
    requesting_user = users_collection.find_one({"username": current_user}) if current_user else None
    is_admin = data.get("isAdmin", False)
    
    if not (requesting_user and requesting_user.get("isAdmin", False)):
        is_admin = False
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    user_data = {
        "username": data['username'],
        "password_hash": hashed_password,
        "isAdmin": is_admin,  
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
        {"username": data['username'], "deletedAt": {"$exists": False}}
    )
 
    if user and check_password_hash(user['password_hash'], data['password']):
        access_token = create_access_token(identity=user['username'])
        return jsonify({"access_token": access_token, "isAdmin": user.get("isAdmin", False), "success": True})

    return jsonify({"error": "error.invalid.credentials"}), 401