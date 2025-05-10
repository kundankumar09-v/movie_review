from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(255), default='https://via.placeholder.com/150?text=User')
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship with reviews
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_url = db.Column(db.String(255), nullable=True)
    backdrop_url = db.Column(db.String(255), nullable=True)  # Added for background images
    trailer_url = db.Column(db.String(255), nullable=True)   # Added for movie trailers
    avg_rating = db.Column(db.Float, default=0.0)            # Added to store average rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade="all, delete-orphan")

    def update_avg_rating(self):
        reviews = Review.query.filter_by(movie_id=self.id).all()
        if reviews:
            total = sum(review.rating for review in reviews)
            self.avg_rating = round(total / len(reviews), 1)
        else:
            self.avg_rating = 0.0
    
    def __repr__(self):
        return f"Movie('{self.title}', '{self.year}')"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Added user relationship
    
    # Keeping author field for backwards compatibility but it will be populated from user relationship
    @property
    def author(self):
        if hasattr(self, 'user') and self.user:
            return self.user.username
        return "Anonymous"
        
    def __repr__(self):
        return f"Review('{self.rating}', '{self.author}', '{self.created_at}')"

class WatchList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define a unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='_user_movie_watchlist_uc'),)
