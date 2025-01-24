from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, User, Article

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class Home(Resource):
    def get(self):
        return {"message": "Welcome to the home page"}, 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            session['user_id'] = user.id
            return jsonify(user.to_dict()), 200
        return jsonify({'error': 'Invalid credentials'}), 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out successfully'}), 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return jsonify(user.to_dict()), 200
        return jsonify({'error': 'No user logged in'}), 401

class ClearSession(Resource):
    def delete(self):
        session.clear()
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return jsonify(articles), 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1
        article = Article.query.filter(Article.id == id).first()
        if article:
            return jsonify(article.to_dict()), 200
        return jsonify({'error': 'Article not found'}), 404

api.add_resource(Home, '/')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)