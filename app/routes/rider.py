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

@rider_bp.route('/my_trips', methods=['GET'])
@jwt_required()
def my_trips():
    rider_id = get_jwt_identity()
    
    trips = list(mongo.db.trips.find({"rider_id": ObjectId(rider_id)}))

    for trip in trips:
        trip['_id'] = str(trip['_id'])
        trip['rider_id'] = str(trip['rider_id'])
        if 'driver_id' in trip:
            trip['driver_id'] = str(trip['driver_id']) if trip['driver_id'] else None

    return jsonify(trips=trips), 200
    