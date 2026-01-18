#!/usr/bin/env python3
from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# ----------------------------
# Clear Session
# ----------------------------
class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

# ----------------------------
# Authentication
# ----------------------------
class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()
        if user:
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 200)
        return {}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return make_response(jsonify(user.to_dict()), 200)
        return {}, 401

# ----------------------------
# Member-only Articles
# ----------------------------
class MemberOnlyIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {}, 401

        articles = Article.query.filter(Article.is_member_only == True).all()
        articles_json = [article.to_dict() for article in articles]
        return make_response(jsonify(articles_json), 200)

class MemberOnlyArticle(Resource):
    def get(self, id):
        if not session.get('user_id'):
            return {}, 401

        # Fetch article by ID regardless of member_only, since user is logged in
        article = Article.query.filter(Article.id == id).first()

        if not article:
            return {}, 404

        return make_response(jsonify(article.to_dict()), 200)


api.add_resource(ClearSession, '/clear')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(MemberOnlyIndex, '/members_only_articles')
api.add_resource(MemberOnlyArticle, '/members_only_articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
