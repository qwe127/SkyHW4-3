# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)

    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")

    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# movie schemas
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


# director schemas
class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


# genre schemas
class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# namespaces
api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

db.create_all()


# first 5 movies
@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie).join(Genre).limit(5).all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


# pages
@movie_ns.route('/page=<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        if mid == 1:
            all_movies = db.session.query(Movie).join(Genre).limit(5).all()
            return movies_schema.dump(all_movies), 200
        if mid >= 2:
            all_movies = db.session.query(Movie).join(Genre).limit(5).offset((mid - 1) * 5).all()
            return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


# movies filtered by director id
@movie_ns.route('/director_id=<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        movies_filtered = db.session.query(Movie).filter(Movie.director_id.like(mid))
        return movies_schema.dump(movies_filtered), 200


# movies filtered by genre id
@movie_ns.route('/genre_id=<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        movies_filtered = db.session.query(Movie).filter(Movie.genre_id.like(mid))
        return movies_schema.dump(movies_filtered), 200


# one movie
@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid):
        movie = db.session.query(Movie).get(mid)
        req_json = request.json

        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)

        db.session.delete(movie)
        db.session.commit()
        return "", 204


# directors
@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)
        return "", 201


# one director
@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404


# all genres
@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


# filter by genre and titles (couldn't make it with "Scheme" method)
@genre_ns.route('/<int:gid>')
class DirectorView(Resource):
    def get(self, gid):
        try:
            result = []
            genre_list = db.session.query(Genre.name, Movie.title).join(Movie).filter(Genre.id == gid)
            for genre in genre_list:
                result.append({
                    "genre": genre.name,
                    "title": genre.title
                })
            return jsonify(result)
        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
