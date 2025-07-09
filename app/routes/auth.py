from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import mongo

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if mongo.db.users.find_one({"email": data['email']}):
        return jsonify({"msg": "User already exists"}), 400
    
    hashed_password = generate_password_hash(data['password'])
    mongo.db.users.insert_one({
        "email": data['email'],
        "password": hashed_password,
        "role": data.get('role', 'rider')  # Default to 'rider'
    })

    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({'email': data['email']})
    
    if user and check_password_hash(user['password'], data['password']):
        user_id = str(user['_id'])  # ensure it's a string
        access_token = create_access_token(identity=user_id)
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Invalid credentials"}), 401