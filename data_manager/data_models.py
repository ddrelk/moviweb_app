from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))

    # Define a one-to-many relationship between User and Movie
    movies = db.relationship('Movie', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'id = {self.id},name = {self.name}, email = {self.email}'

    def __str__(self):
        return f'name={self.name}'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String)
    title = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    year = db.Column(db.Integer)
    poster = db.Column(db.String(200))
    director = db.Column(db.String(100))
    movie_link = db.Column(db.String(200))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))

    def __str__(self):
        return f'movie_id={self.movie_id}, title={self.title}'
