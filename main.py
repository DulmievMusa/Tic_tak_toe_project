import random
from flask import Flask, render_template, redirect, url_for, request, abort, make_response, jsonify
from data import db_session
from flask_restful import reqparse, abort, Api, Resource
from data.users import User
from data import users_resources
db_session.global_init("db/main.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_tic_tac_toe_key'
api = Api(app)
api.add_resource(users_resources.UserListResource, '/api/users')
api.add_resource(users_resources.UserResource, '/api/user/<int:user_id>')


@app.route('/test_reload')
def index():
    return render_template('auto-reload_test.html', num=random.random(), need=True)


def main():
    app.run()


if __name__ == '__main__':
    main()