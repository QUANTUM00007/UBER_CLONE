from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager  
from flask_socketio import SocketIO
from app.routes import auth, rider, driver

mongo = PyMongo()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins='*')

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    mongo.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(rider.bp)
    app.register_blueprint(driver.bp)

    return app