import flask
from flask import jsonify, url_for, session, render_template
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
    game_id = session.get('game_id', '')
    if not game_id:
        return jsonify({'error': 404})
    if is_game_full(game_id):
        return jsonify({'response': 'True'})
    return jsonify({'response': 'False'})


@blueprint.route('/api/get_table_matrix')
def get_table_matrix_api():
    game_id = session.get('game_id', '')
    if not game_id:
        return jsonify({'error': 404})
    matrix = get_matrix(game_id)
    images_matrix = to_images_matrix(matrix)
    return render_template('game_table.html', matrix=images_matrix)


@blueprint.route('/api/is_matrix_change')
def is_matrix_change_api():
    if not session.get('game_id', ''):
        return jsonify({'error': 404})
    if session['str_matrix'] != get_str_matrix(session['game_id']):
        session['str_matrix'] = get_str_matrix(session['game_id'])
        return jsonify({'response': 'True'})
    else:
        return jsonify({'response': 'False'})


@blueprint.route('/api/cell_pressed/<int:index>')
def cell_pressed_api(index):
    return str(index)