from app import app, db
from models import Movie, Review, User, WatchList

def init_db():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
        
        # Check if there are movies in the database
        if Movie.query.count() == 0:
            print("Adding sample movies...")
            
            # Create a demo user first
            demo_user = User(
                username="MovieFan123",
                email="demo@example.com",
                bio="Movie enthusiast and critic. I love discussing cinema!"
            )
            demo_user.set_password("password123")
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user created successfully!")
            
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
            
            db.session.commit()
            print("Sample movies added successfully!")
            
            # Add sample reviews
            movies = Movie.query.all()
            sample_reviews = [
                {
                    "movie_id": movies[0].id,
                    "content": "This is an absolute masterpiece. The storytelling is impeccable, and the performances are outstanding. A true classic that deserves all the praise it gets.",
                    "rating": 10
                },
                {
                    "movie_id": movies[1].id,
                    "content": "One of the most influential films ever made. The direction, acting, and screenplay are all perfect. A must-watch for any film enthusiast.",
                    "rating": 9
                },
                {
                    "movie_id": movies[2].id,
                    "content": "Tarantino at his best. The non-linear storytelling and brilliant dialogue make this a standout film of the 90s.",
                    "rating": 8
                }
            ]
            
            for review_data in sample_reviews:
                review = Review(
                    content=review_data["content"],
                    rating=review_data["rating"],
                    movie_id=review_data["movie_id"],
                    user_id=demo_user.id
                )
                db.session.add(review)
            
            db.session.commit()
            print("Sample reviews added successfully!")
            
            # Update average ratings for all movies
            for movie in movies:
                movie.update_avg_rating()
            
            db.session.commit()
            print("Movie ratings updated successfully!")

if __name__ == "__main__":
    init_db()
