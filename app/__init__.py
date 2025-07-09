from flask import Flask, app
from app.extensions import mongo, jwt, socketio
from app.routes import auth, rider, driver


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    mongo.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(rider.rider_bp)
    # app.register_blueprint(driver.driver_bp)

    @app.route('/')
    def index():
        return 'Uber Clone Backend is Running!'  # ✅ Add this line

    return app
