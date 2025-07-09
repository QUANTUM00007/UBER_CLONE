from math import e
from flask import Blueprint, render_template, request, redirect, flash, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from app.extensions import mongo
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import get_distance_km  # Assuming this is a utility function for distance calculation

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/rider_dashboard')
def rider_dashboard():
    if session.get('role') != 'rider':
        return redirect('/login')
    return render_template('rider_dashboard.html', name=session.get('name'))

@ui_bp.route('/request_ride', methods=['POST'])
def request_ride():
    if session.get('role') != 'rider':
        return redirect('/login')

    ride = {
        "rider_id": ObjectId(session.get('user_id')),
        "pickup": request.form['pickup'],
        "drop": request.form['drop'],
        "status": "requested"
    }
    mongo.db.trips.insert_one(ride)
    flash("Ride requested successfully!", "success")
    return redirect('/rider_dashboard')

@ui_bp.route('/driver_dashboard')
def driver_dashboard():
    if session.get('role') != 'driver':
        return redirect('/login')

    driver_id = ObjectId(session.get('user_id'))

    available_rides = list(mongo.db.trips.find({"status": "requested"}))
    accepted_rides = list(mongo.db.trips.find({"status": "accepted", "driver_id": driver_id}))
    ongoing_rides = list(mongo.db.trips.find({"status": "ongoing", "driver_id": driver_id}))

    for ride in available_rides + accepted_rides + ongoing_rides:
        ride['_id'] = str(ride['_id'])
        ride['rider_id'] = str(ride['rider_id'])

    return render_template(
        'driver_dashboard.html',
        name=session.get('name'),
        available_rides=available_rides,
        accepted_rides=accepted_rides,
        ongoing_rides=ongoing_rides
    )

@ui_bp.route('/accept_ride/<ride_id>', methods=['POST'])
def accept_ride_ui(ride_id):
    if session.get('role') != 'driver':
        return redirect('/login')

    try:
        ride_object_id = ObjectId(ride_id)
    except:
        flash("Invalid ride ID", "danger")
        return redirect('/driver_dashboard')

    trip = mongo.db.trips.find_one({"_id": ride_object_id})

    if not trip:
        flash("Ride not found", "danger")
        return redirect('/driver_dashboard')

    if trip['status'] != 'requested':
        flash("This ride is no longer available", "warning")
        return redirect('/driver_dashboard')

    mongo.db.trips.update_one(
        {"_id": ride_object_id},
        {
            "$set": {
                "status": "accepted",
                "driver_id": ObjectId(session.get('user_id'))
            }
        }
    )

    flash("Ride accepted successfully!", "success")
    return redirect('/driver_dashboard')

@ui_bp.route('/start_ride/<trip_id>', methods=['POST'])
def start_ride_ui(trip_id):
    if session.get('role') != 'driver':
        return redirect('/login')

    try:
        trip_object_id = ObjectId(trip_id)
    except:
        flash("Invalid trip ID", "danger")
        return redirect('/driver_dashboard')

    trip = mongo.db.trips.find_one({"_id": trip_object_id})

    if not trip:
        flash("Trip not found", "danger")
        return redirect('/driver_dashboard')

    if trip.get('driver_id') != ObjectId(session.get('user_id')):
        flash("This trip is not assigned to you", "danger")
        return redirect('/driver_dashboard')

    if trip['status'] != 'accepted':
        flash(f"Trip cannot be started. Current status: {trip['status']}", "warning")
        return redirect('/driver_dashboard')

    mongo.db.trips.update_one(
        {"_id": trip_object_id},
        {"$set": {"status": "ongoing"}}
    )

    flash("Ride started successfully!", "success")
    return redirect('/driver_dashboard')

from app.utils import get_distance_km  # helper if using Google Maps

@ui_bp.route('/complete_ride/<trip_id>', methods=['POST'])
def complete_ride_ui(trip_id):
    if session.get('role') != 'driver':
        return redirect('/login')

    try:
        trip_object_id = ObjectId(trip_id)
    except:
        flash("Invalid trip ID", "danger")
        return redirect('/driver_dashboard')

    trip = mongo.db.trips.find_one({"_id": trip_object_id})

    if not trip:
        flash("Trip not found", "danger")
        return redirect('/driver_dashboard')

    if trip.get('driver_id') != ObjectId(session.get('user_id')):
        flash("You are not assigned to this trip", "danger")
        return redirect('/driver_dashboard')

    if trip['status'] != 'ongoing':
        flash("Only ongoing rides can be completed", "warning")
        return redirect('/driver_dashboard')

    # 🧮 Fare calculation
    pickup = trip['pickup']
    drop = trip['drop']
    try:
        distance_km = get_distance_km(pickup, drop)
    except Exception as e:
        print("Distance fetch error:", e)
        distance_km = 5

    base_fare = 30
    per_km_rate = 10
    fare = base_fare + (distance_km * per_km_rate)

    mongo.db.trips.update_one(
        {"_id": trip_object_id},
        {"$set": {"status": "completed", "fare": round(fare, 2)}}
    )

    flash(f"Ride completed! Fare: ₹{fare:.2f} (Distance: {distance_km} km)", "success")
    return redirect('/driver_dashboard')

@ui_bp.route('/')
def home():
    return render_template('home.html')

@ui_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        user = mongo.db.users.find_one({"email": email, "role": role})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            session['role'] = user['role']
            flash("Logged in successfully", "success")
            return redirect(f"/{role}_dashboard")
        else:
            flash("Invalid credentials", "danger")
            return redirect('/login')
    return render_template('login.html')

@ui_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "email": request.form['email'],
            "password": generate_password_hash(request.form['password']),
            "role": request.form['role']
        }
        if mongo.db.users.find_one({"email": user['email']}):
            flash("User already exists", "danger")
            return redirect('/register')

        mongo.db.users.insert_one(user)
        flash("Registered successfully! Please log in.", "success")
        return redirect('/login')
    return render_template('register.html')
