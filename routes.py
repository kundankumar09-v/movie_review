from flask import render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Movie, Review, User, WatchList
from forms import RegistrationForm, LoginForm, UpdateProfileForm, ReviewForm
import logging
import requests
from urllib.parse import quote

# Home page
@app.route('/')
def index():
    """Home page - shows list of trending movies"""
    featured_movies = Movie.query.order_by(Movie.avg_rating.desc()).limit(4).all()
    recent_movies = Movie.query.order_by(Movie.created_at.desc()).limit(8).all()
    
    # Get some stats for display
    total_movies = Movie.query.count()
    total_reviews = Review.query.count()
    total_users = User.query.count()
    
    return render_template('index.html', 
                           featured_movies=featured_movies,
                           recent_movies=recent_movies,
                           total_movies=total_movies,
                           total_reviews=total_reviews,
                           total_users=total_users)

@app.route('/browse')
def browse():
    """Browse all movies"""
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.order_by(Movie.title).paginate(page=page, per_page=12)
    return render_template('browse.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Movie detail page with reviews"""
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    
    # Check if user has this movie in watchlist
    in_watchlist = False
    if current_user.is_authenticated:
        watchlist_item = WatchList.query.filter_by(
            user_id=current_user.id, movie_id=movie_id).first()
        in_watchlist = watchlist_item is not None
    
    # Similar movies (for now just movies from same director or genre)
    similar_movies = Movie.query.filter(
        (Movie.director == movie.director) | 
        (Movie.genre == movie.genre)
    ).filter(Movie.id != movie.id).limit(4).all()
    
    return render_template('movie.html', 
                           movie=movie, 
                           reviews=reviews, 
                           in_watchlist=in_watchlist,
                           similar_movies=similar_movies)

@app.route('/movie/<int:movie_id>/add_review', methods=['GET', 'POST'])
@login_required
def add_review(movie_id):
    """Add a review for a movie"""
    movie = Movie.query.get_or_404(movie_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user already reviewed this movie
        existing_review = Review.query.filter_by(
            user_id=current_user.id, movie_id=movie_id).first()
        
        if existing_review:
            flash('You have already reviewed this movie. You can edit your review instead.', 'warning')
            return redirect(url_for('movie_detail', movie_id=movie_id))
        
        # Create and save the review
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            movie_id=movie_id,
            user_id=current_user.id
        )
        db.session.add(review)
        
        # Update movie's average rating
        movie.update_avg_rating()
        
        db.session.commit()
        
        flash('Your review has been added!', 'success')
        return redirect(url_for('movie_detail', movie_id=movie_id))
    
    return render_template('add_review.html', form=form, movie=movie)

@app.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit an existing review"""
    review = Review.query.get_or_404(review_id)
    movie = Movie.query.get_or_404(review.movie_id)
    
    # Check if this review belongs to current user
    if review.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = ReviewForm()
    
    if request.method == 'GET':
        # Populate form with existing data
        form.content.data = review.content
        form.rating.data = review.rating
    
    if form.validate_on_submit():
        # Update review
        review.content = form.content.data
        review.rating = form.rating.data
        
        # Update movie's average rating
        movie.update_avg_rating()
        
        db.session.commit()
        
        flash('Your review has been updated!', 'success')
        return redirect(url_for('movie_detail', movie_id=movie.id))
    
    return render_template('edit_review.html', form=form, movie=movie, review=review)

@app.route('/like_review/<int:review_id>', methods=['POST'])
def like_review(review_id):
    """Like a review"""
    review = Review.query.get_or_404(review_id)
    review.likes += 1
    db.session.commit()
    return redirect(url_for('movie_detail', movie_id=review.movie_id))

@app.route('/share/<int:review_id>')
def share(review_id):
    """Share a review page"""
    review = Review.query.get_or_404(review_id)
    movie = Movie.query.get_or_404(review.movie_id)
    share_url = url_for('movie_detail', movie_id=movie.id, _external=True) + f'#review-{review.id}'
    return render_template('share.html', review=review, movie=movie, share_url=share_url)

@app.route('/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    """Add movie to user's watchlist"""
    movie = Movie.query.get_or_404(movie_id)
    
    # Check if already in watchlist
    existing = WatchList.query.filter_by(
        user_id=current_user.id, movie_id=movie_id).first()
    
    if existing:
        flash('Movie is already in your watchlist', 'info')
    else:
        watchlist_item = WatchList(user_id=current_user.id, movie_id=movie_id)
        db.session.add(watchlist_item)
        db.session.commit()
        flash('Added to your watchlist!', 'success')
    
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/watchlist/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    """Remove movie from user's watchlist"""
    watchlist_item = WatchList.query.filter_by(
        user_id=current_user.id, movie_id=movie_id).first()
    
    if watchlist_item:
        db.session.delete(watchlist_item)
        db.session.commit()
        flash('Removed from your watchlist', 'success')
    
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/watchlist')
@login_required
def watchlist():
    """Display user's watchlist"""
    watchlist_items = WatchList.query.filter_by(user_id=current_user.id).all()
    movie_ids = [item.movie_id for item in watchlist_items]
    movies = Movie.query.filter(Movie.id.in_(movie_ids)).all() if movie_ids else []
    
    return render_template('watchlist.html', movies=movies)

# User Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User Profile page"""
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile.html', user=current_user, reviews=reviews)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit User Profile"""
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        if form.profile_image.data and form.profile_image.data.strip():
            current_user.profile_image = form.profile_image.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.profile_image.data = current_user.profile_image
    
    return render_template('edit_profile.html', form=form)

@app.route('/search')
def search():
    """Search for movies"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('browse'))
    
    # Search in title, director, and genre
    movies = Movie.query.filter(
        (Movie.title.ilike(f'%{query}%')) |
        (Movie.director.ilike(f'%{query}%')) |
        (Movie.genre.ilike(f'%{query}%')) |
        (Movie.description.ilike(f'%{query}%'))
    ).all()
    
    return render_template('search_results.html', movies=movies, query=query)

# API endpoint for adding sample data with better images
@app.route('/api/add_sample_data', methods=['POST'])
def add_sample_data():
    """Add sample movies to the database - for development only"""
    try:
        # Only run if the database is empty
        if Movie.query.count() > 0:
            return jsonify({"status": "error", "message": "Database is not empty"})
        
        # Sample movie data with better images
        sample_movies = [
            {
                "title": "The Shawshank Redemption",
                "director": "Frank Darabont",
                "year": 1994,
                "genre": "Drama",
                "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
                "trailer_url": "https://www.youtube.com/embed/6hB3S9bIaco"
            },
            {
                "title": "The Godfather",
                "director": "Francis Ford Coppola",
                "year": 1972,
                "genre": "Crime, Drama",
                "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
                "trailer_url": "https://www.youtube.com/embed/sY1S34973zA"
            },
            {
                "title": "Pulp Fiction",
                "director": "Quentin Tarantino",
                "year": 1994,
                "genre": "Crime, Drama",
                "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                "poster_url": "https://image.tmdb.org/t/p/w500/fIE3lAGcZDV1G6XM5KmuWnNsPp1.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
                "trailer_url": "https://www.youtube.com/embed/s7EdQ4FqbhY"
            },
            {
                "title": "The Dark Knight",
                "director": "Christopher Nolan",
                "year": 2008,
                "genre": "Action, Crime, Drama",
                "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/hkBaDkMWbLaf8B1lsWsKX7Ew3Xq.jpg",
                "trailer_url": "https://www.youtube.com/embed/EXeTwQWrcwY"
            },
            {
                "title": "Inception",
                "director": "Christopher Nolan",
                "year": 2010,
                "genre": "Action, Adventure, Sci-Fi",
                "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
                "trailer_url": "https://www.youtube.com/embed/YoHD9XEInc0"
            },
            {
                "title": "Parasite",
                "director": "Bong Joon-ho",
                "year": 2019,
                "genre": "Comedy, Drama, Thriller",
                "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
                "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
                "trailer_url": "https://www.youtube.com/embed/5xH0HfJHsaY"
            },
            {
                "title": "Interstellar",
                "director": "Christopher Nolan",
                "year": 2014,
                "genre": "Adventure, Drama, Sci-Fi",
                "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
                "trailer_url": "https://www.youtube.com/embed/zSWdZVtXT7E"
            },
            {
                "title": "The Matrix",
                "director": "Lana and Lilly Wachowski",
                "year": 1999,
                "genre": "Action, Sci-Fi",
                "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/original/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
                "trailer_url": "https://www.youtube.com/embed/vKQi3bBA1y8"
            }
        ]
        
        for movie_data in sample_movies:
            movie = Movie(**movie_data)
            db.session.add(movie)
        
        # Create a demo user
        demo_user = User(
            username="MovieFan",
            email="demo@example.com"
        )
        demo_user.set_password("password123")
        db.session.add(demo_user)
        
        db.session.commit()
        
        # Add some initial reviews
        first_movie = Movie.query.first()
        if first_movie and demo_user:
            review = Review(
                content="This is an absolutely brilliant movie! The acting, direction, and screenplay are all top-notch. I would recommend this to anyone who loves cinema.",
                rating=9,
                user_id=demo_user.id,
                movie_id=first_movie.id
            )
            db.session.add(review)
            
            # Update average rating
            first_movie.update_avg_rating()
            db.session.commit()
            
        return jsonify({"status": "success", "message": "Sample data added successfully"})
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding sample data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
