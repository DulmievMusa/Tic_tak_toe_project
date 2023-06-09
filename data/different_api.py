import flask
from flask import jsonify, url_for, session, render_template, request, redirect
from funcs.user_funcs import *
from funcs.game_funcs import *
from flask_login import current_user
from datetime import datetime
from . import db_session


blueprint = flask.Blueprint(
    'different_api',
    __name__,
    template_folder='templates'
)


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
    design = session['design']
    game_id = session.get('game_id', '')
    if not game_id:
        return jsonify({'error': 404})
    matrix = get_matrix(game_id)
    images_matrix = to_images_matrix(matrix, design)
    matrix_with_indexes = add_indexes_to_matrix(images_matrix)
    return render_template('game_table.html', matrix=matrix_with_indexes, design=design,
                           game_board=url_for('static', filename='new_design/game_board.png'))


# @blueprint.route('/api/is_matrix_change')
def is_matrix_change_api():
    if not session.get('game_id', ''):
        return jsonify({'error': 404})
    if session['str_matrix'] != get_str_matrix(session['game_id']):
        session['str_matrix'] = get_str_matrix(session['game_id'])
        return jsonify({'response': 'True'})
    else:
        return jsonify({'response': 'False'})


@blueprint.route('/api/cell_pressed/<int:index>')
def cell_pressed_api(index):  # player's move
    if not session.get('game_id', ''):
        return jsonify({'response': 'error'})
    game_id = session['game_id']
    game = get_game(game_id)['game']
    if game['who_move'] != current_user.id or game['winner'] != 0:
        return jsonify({'response': 'not_move'})
    matrix = list(get_str_matrix(game_id))
    if matrix[index] != 'X' and matrix[index] != '0':
        if game['who_move_first'] == current_user.id:
            matrix[index] = 'X'
        else:
            matrix[index] = '0'
        matrix = ''.join(matrix)
        update_matrix(game_id, matrix)
        increase_count(game_id)
        winner = get_who_win(game_id)
        if winner == 'draw':
            return jsonify({'response': 'draw'})
        if winner != 'nothing happened':
            return jsonify({'response': 'end_game'})
        else:
            if winner != -1 or winner != 'draw':
                change_who_move(game_id)
        return jsonify({'response': 'success'})
    return jsonify({'response': 'not_move'})


# @blueprint.route('/api/is_game_finished')
def is_game_finished_api():
    if not session.get('game_id', ''):
        return jsonify({'response': 'error'})
    winner = get_who_win(session['game_id'])
    if winner != 'nothing happened':
        return jsonify({'response': 'end_game'})
    return jsonify({'response': 'nothing happened'})


# @blueprint.route('/api/get_timer')
def get_timer_api():
    last_time = get_last_time(session['game_id'])
    now_time = datetime.now()
    time_delta = now_time - last_time
    if time_delta.total_seconds() >= 30:
        return jsonify({'response': 'loss'})
    return jsonify({'response': str(int(time_delta.total_seconds()))})


@blueprint.route('/api/do_all_game')
def do_all_game():
    slovar = {}
    if not session.get('game_id', ''):
        return jsonify({'error': 404})
    game_id = session['game_id']
    seconds = str(get_timer())  # get timer
    slovar['seconds'] = seconds
    if seconds == 'loss' and get_just_winner(game_id) == 0:  # if timer loss
        slovar['is_game_finished'] = 'end_game'
        winner = get_who_win_if_timer_end(game_id)
        end_game(game_id, winner, seconds)

    if session['str_matrix'] != get_str_matrix(game_id):  # if matrix changed
        session['str_matrix'] = get_str_matrix(game_id)
        slovar['is_matrix_change'] = 'True'
    else:
        slovar['is_matrix_change'] = 'False'

    winner = get_who_win(game_id)
    if winner != 'nothing happened' and winner != 'draw' and winner != -1:  # if winner
        slovar['is_game_finished'] = 'end_game'
        end_game(game_id, winner, seconds)
        opponent_plus, user_plus = get_rating_pluses(game_id)
        if '+' in str(opponent_plus):
            opponent_plus_style = 'color: #9BBC7E;'
        else:
            opponent_plus_style = 'color: #93261D;'
            if str(opponent_plus) == '0':
                opponent_plus = ''
        slovar['opponent_span'] = f'<span style="{opponent_plus_style}">{opponent_plus}</span>'  # opponent rating plus
        slovar['opponent_rating'] = str(session['old_opponent_rating']) + ' '

        if '+' in str(user_plus):
            user_plus_style = 'color: #9BBC7E;'
        else:
            user_plus_style = 'color: #93261D;'
            if str(user_plus) == '0':
                user_plus = ''
        slovar['user_span'] = f'<span style="{user_plus_style}">{user_plus}</span>'  # user rating plus
        slovar['user_rating'] = str(session['old_user_rating']) + ' '

    elif winner == 'nothing happened':
        slovar['is_game_finished'] = 'nothing happened'

    if winner == 'draw' or winner == -1:  # if draw
        slovar['is_game_finished'] = 'draw'
        slovar['is_draw'] = 'True'
        end_game(game_id, -1, seconds)
    else:
        slovar['is_draw'] = 'False'
    slovar['timer_style'] = get_timer_style(game_id, current_user.id)
    slovar['message'] = 'nothing'
    if str(winner) == str(current_user.id):
        slovar['message'] = 'Congratulations! You won the game!'
    elif winner == -1 or winner == 'draw':
        slovar['message'] = "It's a draw"
    elif str(winner) == str(get_opponent_id(game_id, current_user.id)):
        slovar['message'] = 'Loss'

    return jsonify(slovar)


@blueprint.route('/api/play_again')
def play_again_api():  # this is necessary in order to delete searching game from database
    game_id = get_game_where_user_play(current_user.id)
    sp = []
    while True:
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
    return jsonify({'response': 'success'})