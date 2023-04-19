from flask import Flask, render_template, url_for
from flask_restful import Api
from funcs.game_funcs import *
from funcs.different_funcs import *
from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from waitress import serve
from data import different_api
db_session.global_init("db/main.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tIOWsl8TOJysg6DVtDDC0yC9rsw84cBpmy_tic_pglBhZ3sxqzoh5ffFnznvwDwt78KdYwQ_tac_toe_keyRlioN4f5uz2CFRsK0AijUvvQBdJM81HP'
app.register_blueprint(different_api.blueprint)
api = Api(app)
# api.add_resource(users_resources.UserListResource, '/api/users')
# api.add_resource(users_resources.UserResource, '/api/user/<int:user_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


@app.route('/')
def index():
    design_slovar = {'logotype': url_for('static', filename='new_design/logotype.png'),
                     'logout_image': url_for('static', filename='new_design/logout.png')}
    session['design'] = session.get('design', 'new')
    if current_user.is_authenticated:
        delete_searching_game()
        game_id = get_game_where_user_play(current_user.id)
        sp = []
        while True:  # This is necessary in order to remove games from database that the user does not play
            last_game_id = get_game_where_user_played(current_user.id)
            if last_game_id is not None and last_game_id not in sp:
                sp.append(last_game_id)
                remove_from_players_in_game(last_game_id)
            else:
                break
        if game_id is None:
            ga_id = session.get('game_id', False)
            if ga_id and ga_id not in sp:
                remove_from_players_in_game(session['game_id'])
        session['ending_seconds'] = -1
        session['old_opponent_rating'] = -1
        session['old_user_rating'] = -1
    return render_template('main_page.html', current_user=current_user, is_main_page=True, design=session['design'],
                           design_slovar=design_slovar)


@app.route('/game')
@login_required
def game():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    try:
        session['playing'] = session.get('playing', False)
        if session['playing'] is True:
            game_id = get_game_where_user_play(current_user.id)
        else:
            game_id = session.get('game_id', None)
            if game_id is None:
                return redirect('/')
        session['game_id'] = game_id
        if session['old_opponent_rating'] == -1 and session['old_user_rating'] == -1:
            session['old_opponent_rating'] = get_user(get_opponent_id(game_id, current_user.id))['user']['rating']
            session['old_user_rating'] = get_user(current_user.id)['user']['rating']
        opponent_id = get_opponent_id(session['game_id'], current_user.id)
        opponent_list = get_short_user_list(opponent_id)
        user_list = get_short_user_list(current_user.id)
        session['str_matrix'] = ''
        return render_template('game.html', opponent=opponent_list, user=user_list, design=session['design'])
    except Exception as e:
        print(e)
        return redirect('/')


@app.route('/game_search')
@login_required
def game_search():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    design_slovar = {'logotype': url_for('static', filename='new_design/logotype.png'),
                     'logout_image': url_for('static', filename='new_design/logout.png')}

    init_or_join_game(current_user.id)
    return render_template('game_search_page.html', design=session['design'],
                           design_slovar=design_slovar)


@app.route('/register', methods=['GET', 'POST'])
def register():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    design_slovar = {'logotype': url_for('static', filename='new_design/logotype.png'),
                     'logout_image': url_for('static', filename='new_design/logout.png')}
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        if len(form.password.data) < 5:
            return render_template('register_form.html', title='Registration',
                                   form=form, message="Password must be 5 characters or more",
                                   design=session['design'],
                                   design_slovar=design_slovar)
        if len(form.name.data) > 12:
            return render_template('register_form.html', title='Registration',
                                   form=form, message="Name must be less than 12 characters",
                                   design=session['design'],
                                   design_slovar=design_slovar)
        if len(form.country.data) > 15:
            return render_template('register_form.html', title='Registration',
                                   form=form, message="Country must be less than 15 characters",
                                   design=session['design'],
                                   design_slovar=design_slovar)
        if not is_lat_letters_all(form.country.data):
            return render_template('register_form.html', title='Registration',
                                   form=form, message="The country must be only from Latin letters and spaces",
                                   design=session['design'],
                                   design_slovar=design_slovar)
        if not is_lat_letters_all(form.name.data):
            return render_template('register_form.html', title='Registration',
                                   form=form, message="The name must be only from Latin letters and spaces",
                                   design=session['design'],
                                   design_slovar=design_slovar)
        if form.password.data != form.password_again.data:
            return render_template('register_form.html', title='Registration',
                                   form=form, message="Passwords isn't same", design=session['design'],
                                   design_slovar=design_slovar)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            db_sess.close()
            return render_template('register_form.html', title='Registration',
                                   form=form, message="This user already exists", design=session['design'],
                                   design_slovar=design_slovar)
        db_sess.close()
        add_user({
                 'name': form.name.data,
                 'rating': 50,
                 'country': form.country.data[0].upper() + form.country.data[1:],
                 'email': form.email.data,
                 'password': form.password.data})
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        login_user(user, remember=True)
        session['playing'] = False
        session['game_id'] = -1
        return redirect('/')
    return render_template('register_form.html', title='Registration', form=form, design=session['design'],
                           design_slovar=design_slovar)


@app.route('/login', methods=['GET', 'POST'])
def login():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    design_slovar = {'logotype': url_for('static', filename='new_design/logotype.png'),
                     'logout_image': url_for('static', filename='new_design/logout.png')}
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session['playing'] = False
            session['game_id'] = -1
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password", form=form, design=session['design'],
                               design_slovar=design_slovar)
    return render_template('login.html', title='Authorization', form=form, design=session['design'],
                           design_slovar=design_slovar)


@app.route('/logout')
@login_required
def logout():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    design_old = session['design']
    session.clear()  # may be deleted
    logout_user()
    session['design'] = design_old
    return redirect("/")


@app.route('/change_design')
def change_design_page():
    design = session.get('design', False)
    if not design:
        return redirect('/')

    session['design'] = 'new' if session['design'] == 'old' else 'old'
    return redirect('/')


def main():
    serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()