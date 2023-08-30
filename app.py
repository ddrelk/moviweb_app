from flask import Flask, render_template, request, url_for, redirect, session
from moviweb_app.data_manager.json_storage_manager import JSONDataManager
from api_extractor import get_imdb_link, data_extractor
from moviweb_app.id_password_handler import generate_password_hash, id_generator
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from moviweb_app.login_handler import User

app = Flask(__name__)
data_manager = JSONDataManager("data/movies.json")
app.secret_key = '0ac93239bf1b653ee7a5392e84e3b703'
login_manager = LoginManager(app)


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/movie')
def movie_details():
    return render_template('movie_details.html')


@login_manager.user_loader
def load_user(user_id):
    # Implement logic to load a user from your data source
    # For example, if users_data is a list of user dictionaries
    user_data = data_manager.get_user_data()
    user = next((user for user in user_data if user['id'] == user_id), None)

    if user:
        return User(user)
    else:
        return None


@app.route('/users')
def list_users():
    try:
        users = data_manager.get_user_data()
        return render_template('users.html', users=users)
    except TypeError as te:
        print(f"Error: {str(te)}")
        return render_template('error.html', error_message="Error retrieving users data")
    except IOError as e:
        error_message = "An error occurred while retrieving user data."
        print(f"IOError: {str(e)}")
        return render_template('error.html', error_message=error_message)
    except RuntimeError as e:
        error_message = "An unexpected error occurred."
        print(f"Error: {str(e)}")
        return render_template('error.html', error_message=error_message)


@app.route('/users/<user_id>')
@login_required
def list_user_movies(user_id):
    try:
        user_name = data_manager.get_user_name(user_id)
        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', movies=movies, user_name=user_name, user_id=user_id)
    except TypeError as te:
        print(f"Error: {str(te)}")
        return render_template('error.html', error_message="Error retrieving user data")
    except IOError as e:
        error_message = "An error occurred while retrieving the user data."
        print(f"IOError: {str(e)}")
        return render_template('error.html', error_message=error_message)
    except RuntimeError as e:
        error_message = "An unexpected error occurred."
        print(f"Error: {str(e)}")
        return render_template('error.html', error_message=error_message)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form.get('name')
        email = request.form.get('email')
        user_password = request.form.get('password')
        user_id = id_generator()

        try:
            hashed_password = generate_password_hash(user_password)
            if data_manager.add_user(user_name, hashed_password, user_id, []):
                session['user_id'] = user_id
                session['username'] = user_name
                return redirect(url_for('login', username=user_name))

        except ValueError as e:
            return render_template('add_user.html', error_message=str(e))
        except IOError as e:
            error_message = "An error occurred while adding a new user."
            print(f"IOError: {str(e)}")
            return render_template('error.html', error_message=error_message)
        except RuntimeError as e:
            error_message = "An unexpected error occurred."
            print(f"Error: {str(e)}")
            return render_template('error.html', error_message=error_message)
    return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie = request.form.get('movie')
        movie_info = data_extractor(movie)
        movie_link = get_imdb_link(movie)
        try:
            if movie_info is not None and 'Title' in movie_info and 'Year' in movie_info and 'Director' in movie_info:
                title = movie_info.get("Title")
                if len(movie_info['Ratings']) > 0:
                    rating = float(movie_info['Ratings'][0]['Value'].split("/")[0])
                else:
                    rating = None

                year_str = movie_info.get('Year')
                if year_str.isdigit():
                    year = int(year_str)
                else:
                    error_message = "Failed to retrieve movie information. Please try a different movie"
                    return render_template('error.html', error_message=error_message)

                poster = movie_info.get('Poster')
                director = movie_info.get('Director')
                movie_id = id_generator()

                data_manager.add_movie(user_id, movie_id, title, rating, year, poster, director, movie_link)

                return redirect(url_for('list_user_movies', user_id=user_id))
            else:
                error_message = "Failed to retrieve movie information. Please make sure the movie exists."
                return render_template('error.html', error_message=error_message)

        except ValueError as e:
            error_message = str(e)
            return render_template('error.html', error_message=error_message)

        except IOError as e:
            error_message = "An error occurred while adding a movie."
            print(f"IOError: {str(e)}")
            return render_template('error.html', error_message=error_message)
        except RuntimeError as e:
            error_message = "An unexpected error occurred."
            print(f"Error: {str(e)}")
            return render_template('error.html', error_message=error_message)

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    user_movie_list = data_manager.get_user_movies(user_id)
    movie_to_update = None
    for movie in user_movie_list:
        if movie['id'] == movie_id:
            movie_to_update = movie
            break

    if movie_to_update is None:
        # Handle possible errors with the movie id
        error_message = "Sorry, we could not find that movie!"
        return render_template('general_error.html', error_message=error_message)

    if request.method == 'POST':
        title = movie_to_update['title']
        updated_director = request.form['director']
        updated_year = request.form['year']
        updated_rating = request.form['rating']
        updated_poster_link = request.form['poster']
        updated_imdb_link = request.form['imdb_link']
        new_movie_id = id_generator()
        try:
            data_manager.update_movie(user_id, movie_id, new_movie_id, title, updated_rating,
                                      updated_year, updated_poster_link, updated_director, updated_imdb_link)

            return redirect(url_for('list_user_movies', user_id=user_id))

        except ValueError as ve:
            error_message = "An error occurred while updating the movie."
            print(f"ValueError: {str(ve)}")
            return render_template('error.html', error_message=error_message)

        except IOError as e:
            error_message = "An error occurred while updating the movie."
            print(f"IOError: {str(e)}")
            return render_template('error.html', error_message=error_message)

        except RuntimeError as e:
            error_message = "An unexpected error occurred."
            print(f"Error: {str(e)}")
            return render_template('error.html', error_message=error_message)

    return render_template('update_movie.html', movie_id=movie_id, user_id=user_id, movie=movie_to_update)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    if request.method == 'POST':
        try:
            data_manager.delete_movie(user_id, movie_id)
            return redirect(url_for('list_user_movies', user_id=user_id, movie_id=movie_id))

        except (ValueError, TypeError):
            # Handle possible errors with the movie id
            error_message = "Sorry, we could not find that movie!"
            return render_template('error.html', error_message=error_message)
        except RuntimeError as re:
            print(f"Error: {str(re)}")
            return render_template('error.html', error_message=re)

    error_message = "Sorry, this page does not support GET requests"
    return render_template('error.html', error_message=error_message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = data_manager.verify_user(username, password)
            if user:
                user_id = user['id']
                user_obj = load_user(user_id)  # Create a User object
                login_user(user_obj)  # Log the user in
                return redirect(url_for('list_user_movies', user_id=user_id))
            else:
                error_message = "Invalid credentials. Please try again."
                return render_template('login.html', error_message=error_message)
        except IOError as e:
            error_message = "An error occurred while logging in."
            print(f"IOError: {str(e)}")
            return render_template('error.html', error_message=error_message)
        except RuntimeError as e:
            error_message = "An unexpected error occurred."
            print(f"Error: {str(e)}")
            return render_template('error.html', error_message=error_message)

    return render_template('login.html')


@app.route('/users/<user_id>/manage_account', methods=['GET'])
@login_required
def manage_account(user_id):
    """Renders the manage account page for a specific user."""
    return render_template('manage_account.html', user_id=user_id)


@app.route('/users/<user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    """Deletes a user and all its associated movies """
    if request.method == 'POST':
        user_password = request.form.get('password')
        user_password_2 = request.form.get('confirm_password')

        if user_password == user_password_2:
            try:
                current_user_id = current_user.id
                if current_user_id == user_id:
                    session.clear()
                    return redirect(url_for('login'))
                else:
                    error_message = "You are not authorized to delete this user."
                    return render_template('error.html', error_message=error_message)
            except ValueError as e:
                error_message = str(e)
                return render_template('error.html', error_message=error_message)
            except RuntimeError as e:
                error_message = str(e)
                return render_template('error.html', error_message=error_message)
    return render_template('delete_user.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
