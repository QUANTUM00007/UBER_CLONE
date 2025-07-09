from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import mongo
from bson import ObjectId

driver_bp = Blueprint('driver', __name__, url_prefix='/api/driver')

@driver_bp.route('/available_rides', methods=['GET'])
@jwt_required()
def available_ride():
    # fetch all available rides

    trips = list(mongo.db.trips.find({"status": "requested"}))

    for trip in trips:
        trip['_id'] = str(trip['_id'])
        trip['rider_id'] = str(trip['rider_id'])
    
    return jsonify(trips=trips), 200

@driver_bp.route('/accept_ride/<trip_id>', methods=['POST'])
@jwt_required()
def accept_ride(trip_id):
    driver_id = get_jwt_identity()  

    trip = mongo.db.trips.find_one({"_id": ObjectId(trip_id), "status": "requested"})

    if not trip:
        return jsonify({"msg": "Trip not found or already accepted"}), 404

    if trip['status'] != 'requested':
        return jsonify({"msg": "Trip is already accepted or completed"}), 400

    # Update the trip
    mongo.db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {
            "$set": {
                "driver_id": ObjectId(driver_id),
                "status": "accepted"
            }
        }
    )

    return jsonify({"msg": "Trip accepted successfully"}), 200

@driver_bp.route('/start_trip/<trip_id>', methods=['POST'])
@jwt_required()
def start_trip(trip_id):
    driver_id = get_jwt_identity()  

    trip = mongo.db.trips.find_one({"_id": ObjectId(trip_id), "status": "accepted", "driver_id": ObjectId(driver_id)})

    if not trip:
        return jsonify({"msg": "Trip not found"}), 404

    if trip.get('driver_id') != ObjectId(driver_id):
        return jsonify({"msg": "This trip is not assigned to you"}), 403

    if trip['status'] != 'accepted':
        return jsonify({"msg": "Cannot start ride. Current status: {}".format(trip['status'])}), 400

    # Update the trip status to ongoing
    mongo.db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "ongoing"}}
    )

    return jsonify({"msg": "Trip started successfully"}), 200

@driver_bp.route('/complete_trip/<trip_id>', methods=['POST'])
@jwt_required()
def complete_trip(trip_id):
    driver_id = get_jwt_identity()  

    trip = mongo.db.trips.find_one({"_id": ObjectId(trip_id), "status": "ongoing", "driver_id": ObjectId(driver_id)})

    if not trip:
        return jsonify({"msg": "Trip not found"}), 404

    if trip.get('driver_id') != ObjectId(driver_id):
        return jsonify({"msg": "This trip is not assigned to you"}), 403

    if trip['status'] != 'ongoing':
        return jsonify({"msg": "Cannot complete ride. Current status: {}".format(trip['status'])}), 400

    # Update the trip status to completed
    mongo.db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "completed"}}
    )

    return jsonify({"msg": "Trip completed successfully"}), 200