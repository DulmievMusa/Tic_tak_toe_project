import flask
from flask import jsonify, url_for, session
from funcs.user_funcs import *
from funcs.game_funcs import *
from . import db_session


blueprint = flask.Blueprint(
    'different_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/loading_count')
def get_loading_count_api():
    loading_count = get_loading_frame()
    return f'<img src="{url_for("static", filename=f"images/loading_sprites/loading_{loading_count + 1}.gif")}">'


@blueprint.route('/api/is_game_full')
def is_game_full_api():
    if is_game_full(session['game_id']):
        return jsonify({'response': 'True'})
    return jsonify({'response': 'False'})
