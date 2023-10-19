from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface
from .data_models import Movie, User, Review
from moviweb_app.id_password_handler import check_password_hash


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)

    def get_all_users(self):
        try:
            db = self.db
            users = db.session.query(User.name).all()
            return [name for (name,) in users]  # Extract names from the result
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching users: {str(e)}")
            return []

    def get_user_name(self, user_id):
        try:
            db = self.db
            user = db.session.query(User).filter_by(id=user_id).first()
            if user:
                return user.name
            else:
                return None  # User with the specified ID not found
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching user name: {str(e)}")
            return None  # Error occurred

    def get_user_movies(self, user_id):
        try:
            db = self.db
            user_movies = db.session.query(Movie).filter(Movie.user_id == user_id).all()
            return user_movies
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching user movies: {str(e)}")
            return []

    def add_movie(self, user_id, movie_id, title, rating, year, poster, director, movie_link):
        try:
            db = self.db

            # Create a new Movie instance
            new_movie = Movie(
                movie_id=movie_id,
                title=title,
                rating=rating,
                year=year,
                poster=poster,
                director=director,
                movie_link=movie_link,
                user_id=user_id
            )

            # Add the new movie to the database
            db.session.add(new_movie)
            db.session.commit()

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while adding a movie: {str(e)}")
            return None  # Error occurred, movie not added

    def add_user(self, user_name, encrypted_password, user_id, email):
        try:
            db = self.db

            # Create a new User instance
            new_user = User(
                id=user_id,
                name=user_name,
                password=encrypted_password,
                email=email
            )

            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            return True  # User added successfully
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while adding a user: {str(e)}")
            return None  # Error occurred, user not added

    def update_movie(self, user_id, movie_id, new_movie_id, title, rating, year, poster, director, movie_link):
        try:
            db = self.db

            # Query the existing movie by user_id and movie_id
            existing_movie = db.session.query(Movie).filter(
                (Movie.user_id == user_id) & (Movie.movie_id == movie_id)).first()

            if existing_movie:
                # Update the movie's attributes
                existing_movie.movie_id = new_movie_id
                existing_movie.title = title
                existing_movie.rating = rating
                existing_movie.year = year
                existing_movie.poster = poster
                existing_movie.director = director
                existing_movie.movie_link = movie_link

                # Commit the changes to the database
                db.session.commit()

                return existing_movie  # Return the updated movie object
            else:
                return None  # Movie with the specified user_id and movie_id not found
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while updating a movie: {str(e)}")
            return None  # Error occurred, movie not updated

    def delete_movie(self, user_id, movie_id):
        try:
            db = self.db

            # Query the existing movie by user_id and movie_id
            existing_movie = db.session.query(Movie).filter(
                user_id == user_id, movie_id == movie_id).first()

            if existing_movie:
                # Delete the movie from the database
                db.session.delete(existing_movie)
                db.session.commit()

                return True  # Movie successfully deleted
            else:
                return False  # Movie with the specified user_id and movie_id not found
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while deleting a movie: {str(e)}")
            return False  # Error occurred, movie not deleted

    def delete_user(self, user_id):
        try:
            db = self.db

            # Query the existing user by user_id
            existing_user = db.session.query(User).filter_by(id=user_id).first()

            if existing_user:
                # Delete the user from the database
                db.session.delete(existing_user)
                db.session.commit()

                return True  # User successfully deleted
            else:
                return False  # User with the specified user_id not found
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while deleting a user: {str(e)}")
            return False  # Error occurred, user not deleted

    def get_user_data(self):
        try:
            db = self.db
            users = db.session.query(User).all()

            users_data = []
            for user in users:
                username = user.name
                password = user.password
                user_id = user.id
                users_data.append({'name': username, 'password': password, 'id': user_id})

            return users_data
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching user data: {str(e)}")
            return []

    def update_password(self, user_id, new_password):
        try:
            db = self.db

            # Query the existing user by user_id
            existing_user = db.session.query(User).filter_by(id=user_id).first()

            if existing_user:
                # Update the user's password
                existing_user.password = new_password

                # Commit the changes to the database
                db.session.commit()

                return True  # Password successfully updated
            else:
                return False  # User with the specified user_id not found
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while updating a user's password: {str(e)}")
            return False  # Error occurred, password not updated

    def verify_user(self, username, password):
        try:
            db = self.db

            # Query the user by username
            user = db.session.query(User).filter_by(name=username).first()

            if user:
                # Check if the provided password matches the user's password
                if check_password_hash(user.password, password):
                    return user  # Username and password match
                else:
                    return None  # Password does not match

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while verifying user credentials: {str(e)}")
            return False  # Error occurred

    def check_movie_id_exist(self, movie_id):
        try:
            db = self.db

            # Query the database to check if a movie with the given movie_id exists
            existing_movie = db.session.query(Movie).filter_by(movie_id=movie_id).first()

            # If a movie with the given movie_id exists, return True; otherwise, return False
            return existing_movie is not None

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while checking if a movie exists: {str(e)}")
            return False  # Error occurred, consider the movie doesn't exist

    def add_reviews(self, review_id, user_id, movie_id, rating, likes, publication_date,
                    review_text, review_title,):  # CHECKED
        """Allows the user to publish a review for a certain movie with the given ID"""
        # Check if the movie exists
        try:
            db = self.db
            if not self.check_movie_id_exist(movie_id):
                raise ValueError(f"Movie with not found")

            # Check if the user exists
            user = self.get_user_name(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            new_review = Review(
                review_id=review_id,
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
                likes=likes,
                publication_date=publication_date,
                review_text=review_text,
                review_title=review_title
            )
            db.session.add(new_review)
            db.session.commit()
            return True
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while adding a review: {str(e)}")
            return None  # Error occurred, review not added

    def edit_reviews(self, review_id, user_id, movie_id, rating, review_text, review_title):  # CHECKED
        """Allows a user to edit his movie review"""
        # Check if the movie exists
        try:
            db = self.db
            if not self.check_movie_id_exist(movie_id):
                raise ValueError(f"Movie with not found")

            # Check if the user exists
            user = self.get_user_name(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            existing_review = db.session.query(Review).filter_by(review_id=review_id).first()
            if existing_review:
                existing_review.rating = rating
                existing_review.review_text = review_text
                existing_review.review_title = review_title
                db.session.commit()
                return True
        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while editing a review: {str(e)}")
            return None  # Error occurred, movie review not edited

    def delete_reviews(self, user_id, movie_id, review_id):  # CHECKED
        """deletes a review"""
        # Check if the movie exists
        try:
            db = self.db
            if not self.check_movie_id_exist(movie_id):
                raise ValueError(f"Movie with not found")

            # Check if the user exists
            user = self.get_user_name(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Check if the review exists
            existing_review = db.session.query(Review).filter(
                review_id == review_id).first()
            if not existing_review:
                raise ValueError(f"Review not found with ID {review_id}")

            # Delete the review
            db.session.delete(existing_review)
            db.session.commit()
            return True

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while deleting a movie: {str(e)}")
            return None  # Error occurred, movie not deleted

    def get_movie_details(self, movie_id):
        """Retrieves a movie by its ID from the database."""
        try:
            db = self.db
            movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
            if movie:
                return movie
            else:
                raise ValueError(f"Movie not found")

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching movie details: {str(e)}")
            return None  # Error occurred

    def get_review_info(self, review_id):
        """Retrieves a review by its ID from the database."""
        try:
            db = self.db
            review = db.session.query(Review).filter(Review.review_id == review_id).first()
            if review:
                return review
            else:
                raise ValueError(f"Review not found")

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching review details: {str(e)}")
            return None  # Error occurred

    def get_all_movie_reviews(self, movie_id):  # CHECKED
        """retrieves all the movie info and reviews for a movie with the provided ID"""
        try:
            db = self.db
            reviews = db.session.query(Review).filter(Review.movie_id == movie_id).all()
            return reviews

        except Exception as e:
            # Handle exceptions (e.g., database connection errors) here
            print(f"Error while fetching movie reviews: {str(e)}")
            return []  # Return an empty list if an error occurred
