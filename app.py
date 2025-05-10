import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'  # Name of the route for login
login_manager.login_message_category = 'info'

# Initialize Flask app
app = Flask(__name__)
# Make sure we have a database URI, use SQLite as fallback if needed
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Fix potential "postgres://" to "postgresql://" issue
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logging.debug(f"Using PostgreSQL database: {database_url}")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviecritic.db'
    logging.debug("Using SQLite database")
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize the extensions with the app
db.init_app(app)
login_manager.init_app(app)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    # Import models after db initialization to avoid circular imports
    from models import User, Movie, Review, WatchList
    db.create_all()
