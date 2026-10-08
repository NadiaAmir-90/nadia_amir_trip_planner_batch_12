import os

from flask import Flask,jsonify

from database.db import db
from models.trip import Trip
from routes.trip_routes import trip_bp
def create_app():

#  creates instances of flask app
  app=Flask(__name__)

# SQLite database configuration 
  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///trip_planner.db"
  )
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

 # SQLalchemy intialize 
  db.init_app(app)

  # creates all tables auto 
  with app.app_context():
    db.create_all()

# Register trip routes 
  app.register_blueprint(trip_bp)
  # globall error handler:
  @app.errorhandler(404)
  def handle_404(error):
    return jsonify({
      "error": "NOT_FOUND",
      "message": "The requested resource was not found"
    }), 404

  @app.errorhandler(405)
  def handle_405(error):
    return jsonify({
      "error": "METHOD_NOT_ALLOWED",
      "message": "HTTP method is not allowed for this endpoint"
    }), 405

# endpoint to check server health
  @app.route("/health",methods=["GET"])

  def heath():
    
    return jsonify(
        {
            "status":"ok"
        }
    ),200
  
  @app.route("/",methods=["GET"])

  def home():

    return jsonify(
        {
            "message":"Welcome to the Trip planner Application !"
        }
    ),200


  return app
