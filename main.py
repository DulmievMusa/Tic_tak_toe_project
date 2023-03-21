import random
from requests import get, post, delete, put
from flask import Flask, render_template, redirect, url_for, request, abort, make_response, jsonify, session
from data import db_session
from flask_restful import reqparse, abort, Api, Resource
from data.users import User
from funcs.user_funcs import *
from funcs.game_funcs import *
# from data import users_resources
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from waitress import serve
db_session.global_init("db/main.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_tic_tac_toe_key'

api = Api(app)
# api.add_resource(users_resources.UserListResource, '/api/users')
# api.add_resource(users_resources.UserResource, '/api/user/<int:user_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/session_test")
def session_test():
    loading_count = session.get('loading_count', 0)
    session['loading_count'] = loading_count + 1
    return make_response(
        f"Вы пришли на эту страницу {loading_count + 1} раз")


@app.route('/test_reload')
def test_reload():
    return render_template('auto-reload_test.html', num=random.random(), need=True)


@app.route('/')
def index():
    return render_template('main_page.html', current_user=current_user)


@app.route('/game_search')
@login_required
def game_search():
    loading_count = session.get('loading_count', 0)
    if loading_count + 1 == 9:
        loading_count = 0
    session['loading_count'] = loading_count + 1
    if not is_user_in_game(current_user.id):
        create_game(current_user.id)
    session['playing'] = True

    return render_template('game_search_page.html',
                           link=url_for('static', filename=f'images/loading_sprites/loading_{loading_count + 1}.gif'))


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
        add_user({
                 'name': form.name.data,
                 'rating': 0,
                 'country': form.country.data,
                 'email': form.email.data,
                 'password': form.password.data})
        return redirect('/')
    return render_template('register_form.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session['playing'] = False
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/logout')
@login_required
def logout():
    session['playing'] = False
    logout_user()
    return redirect("/")


def main():
    app.run()
    # serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()