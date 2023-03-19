import random
from requests import get, post, delete, put
from flask import Flask, render_template, redirect, url_for, request, abort, make_response, jsonify
from data import db_session
from flask_restful import reqparse, abort, Api, Resource
from data.users import User
from data import users_resources
from forms.register_form import RegisterForm
db_session.global_init("db/main.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_tic_tac_toe_key'
api = Api(app)
api.add_resource(users_resources.UserListResource, '/api/users')
api.add_resource(users_resources.UserResource, '/api/user/<int:user_id>')


@app.route('/test_reload')
def test_reload():
    return render_template('auto-reload_test.html', num=random.random(), need=True)


@app.route('/')
def index():
    return render_template('base.html', current_user=False)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_form.html', title='Registration',
                                   form=form, message="Passwords isn't same")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_form.html', title='Registration',
                                   form=form, message="This user already exists")
        post('http://127.0.0.1:5000/api/users',
             json={
                 'name': form.name.data,
                 'rating': 0,
                 'country': form.country.data,
                 'email': form.email.data,
                 'password': form.password.data
             })
        return redirect('/')
    return render_template('register_form.html', title='Registration', form=form)


def main():
    app.run()


if __name__ == '__main__':
    main()