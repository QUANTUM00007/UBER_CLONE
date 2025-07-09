from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

rider_bp = Blueprint('rider', __name__, url_prefix='/api/rider')    

@rider_bp.route('/request_ride', methods=['POST'])
@jwt_required()
def request_ride():
    data = request.get_json()
    user_id = get_jwt_identity()

    pickup = data.get('pickup')
    drop = data.get('drop')

    if not pickup or not drop:  
        return jsonify({"msg": "Pickup and dropoff locations are required"}), 400
    
    trip = {
        'rider_id': ObjectId(user_id),
        'pickup': pickup,
        'drop': drop,
        'status': 'requested',  # other statuses: accepted, ongoing, completed, cancelled
        'requested_at': datetime.now(datetime.now().tzinfo)
    }

    
    result = mongo.db.trips.insert_one(trip)

    return jsonify({"msg": "Ride requested successfully", "ride_id": str(result.inserted_id)}), 201
    