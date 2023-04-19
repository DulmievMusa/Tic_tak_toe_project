from data import db_session
from data.games import Game
from flask import session, url_for
from funcs.user_funcs import *
from random import choice, randint
from datetime import datetime
from flask_login import current_user


def is_game_found(game_id):
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    if not game:
        return False
    return True


def get_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    return {'game': game.to_dict()}


def delete_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.delete(game)
    session.commit()
    session.close()
    return {'success': 'OK'}


def edit_game(game_id, args):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.players_ids = args.get('players_ids', game.players_ids)
    game.who_move = args.get('who_move', game.who_move)
    game.matrix = args.get('matrix', game.matrix)
    game.last_time = args.get('last_time', game.last_time)
    game.waitcount = args.get('waitcount', game.waitcount)
    game.start_time = args.get('start_time', game.start_time)
    game.winner = args.get('winner', game.winner)
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_games():
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    return {'games': [item.to_dict() for item in games]}


def create_game(user_id):
    session = db_session.create_session()
    game = Game(
        players_ids=user_id,
        who_move_first=0,
        who_move=0,
        matrix='YYYYYYYYY',
        count=0,
        winner=0,
        players_in_game=str(current_user.id))
    session.add(game)
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_free_game_id():
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if len(game.players_ids.split()) == 1 and game.winner == 0:
            return game.id
    return None


def add_user_id_to_game(game_id, user_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.players_ids = game.players_ids + ' ' + str(user_id)
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_loading_frame():
    loading_count = session.get('loading_count', 0)
    if loading_count + 1 == 9:
        loading_count = 0
    session['loading_count'] = loading_count + 1
    return loading_count


def init_or_join_game(user_id):
    if not is_user_in_game(user_id) and get_free_game_id() is None \
            and get_game_where_user_play(user_id) is None:  # create new game
        create_game(user_id)
        new_game_id = get_game_where_user_play(user_id)
        session['game_id'] = new_game_id
        session['winner'] = 0
    else:
        if not is_user_in_game(user_id):  # join game
            free_game_id = get_free_game_id()
            session['game_id'] = free_game_id
            add_user_id_to_game(free_game_id, user_id)
            add_user_to_players_in_game(free_game_id)
            opponent_id = get_opponent_id(free_game_id, user_id)
            who_move_id = choice_who_move(user_id, opponent_id)
            set_who_move(free_game_id, who_move_id)
            set_last_time(free_game_id)
            session['winner'] = 0

    session['old_opponent_rt'] = -1
    session['old_user_rt'] = -1
    session['playing'] = True
    session['game_id'] = get_game_where_user_play(user_id)


def is_game_full(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    if len(game.players_ids.split()) == 2:
        return True
    return False


def get_matrix(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    field = list(game.matrix)
    sp = []
    for i in range(0, len(field), 3):
        sp.append(field[i:i + 3])
    return sp


def get_opponent_id(game_id, user_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    players = game.players_ids.split()
    players.remove(str(user_id))
    return players[0]


def to_images_matrix(matrix, design):
    mat = []
    for row in matrix:
        sp = []
        for elem in row:
            if elem == '0':
                if design == 'old':
                    sp.append(url_for('static', filename='images/game_sprites/circle.png'))
                elif design == 'new':
                    sp.append(url_for('static', filename='new_design/circle.png'))
            elif elem == 'X':
                if design == 'old':
                    sp.append(url_for('static', filename='images/game_sprites/cross.png'))
                elif design == 'new':
                    sp.append(url_for('static', filename='new_design/cross.png'))
            else:
                sp.append('space')
        mat.append(sp)
    return mat


def get_str_matrix(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    return game.matrix


def add_indexes_to_matrix(matrix):
    mat = []
    index = -1
    for row in matrix:
        sp = []
        for elem in row:
            index += 1
            sp.append((elem, str(index)))
        mat.append(sp.copy())
    return mat


def update_matrix(game_id, matrix):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.matrix = matrix
    session.commit()
    session.close()


def choice_who_move(user_id, opponent_id):
    return choice([user_id, opponent_id])


def set_who_move(game_id, who_move_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.who_move = who_move_id
    game.who_move_first = who_move_id
    session.commit()
    session.close()


def increase_count(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.count = game.count + 1
    session.commit()
    session.close()


def change_who_move(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    moving = game.who_move
    sp = game.players_ids.split()
    sp.remove(str(moving))
    game.who_move = sp[0]
    game.last_time = datetime.now()
    session.commit()
    session.close()


def get_who_win(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    matrix = get_matrix(game_id)
    game = get_game(game_id)['game']
    if game['winner'] != 0:
        return game['winner']
    x_winner = game['who_move_first']
    o_winner = get_opponent_id(game_id, game['who_move_first'])
    fix, six, thix = 0, 0, 0  # first index x
    fi0, si0, thi0 = 0, 0, 0
    for row in matrix:
        if row == ['X', 'X', 'X']:
            return x_winner
        elif row == ['0', '0', '0']:
            return o_winner
        if row[0] == 'X':
            fix += 1
        elif row[0] == '0':
            fi0 += 1
        if row[1] == 'X':
            six += 1
        elif row[1] == '0':
            si0 += 1
        if row[2] == 'X':
            thix += 1
        elif row[2] == '0':
            thi0 += 1
        if fix == 3 or six == 3 or thix == 3:
            return x_winner
        elif fi0 == 3 or si0 == 3 or thi0 == 3:
            return o_winner
    if matrix[0][0] == 'X' and matrix[1][1] == 'X' and matrix[2][2] == 'X':
        return x_winner
    elif matrix[0][0] == '0' and matrix[1][1] == '0' and matrix[2][2] == '0':
        return o_winner
    if matrix[0][2] == 'X' and matrix[1][1] == 'X' and matrix[2][0] == 'X':
        return x_winner
    elif matrix[0][2] == '0' and matrix[1][1] == '0' and matrix[2][0] == '0':
        return o_winner

    if game['count'] == 9:
        return 'draw'

    return 'nothing happened'


def set_winner(winner, game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.winner = winner
    session.commit()
    session.close()


def end_game(game_id, winner, ending_seconds):
    if session['winner'] != 0:
        return
    session['playing'] = False
    session['ending_seconds'] = ending_seconds
    if winner != -1:
        if not is_winner_in_game(game_id):
            increase_rating(winner, winner)
            increase_rating(get_opponent_id(game_id, winner), winner)
    elif winner == -1:
        pass
    set_winner(winner, game_id)
    session['winner'] = winner


def get_last_time(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    return game.last_time


def get_timer():
    if session['playing'] is False:
        return session['ending_seconds']
    if not is_game_found(session['game_id']):
        return {'error': 404}
    last_time = get_last_time(session['game_id'])
    now_time = datetime.now()
    time_delta = now_time - last_time
    if 15 - time_delta.total_seconds() < 0:
        return 'loss'
    return 15 - int(time_delta.total_seconds())


def get_who_win_if_timer_end(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    winner = get_opponent_id(game_id, game.who_move)
    return winner


def get_who_move(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    return game.who_move


def set_last_time(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.last_time = datetime.now()
    session.commit()
    session.close()


def get_timer_style(game_id, user_id):
    timer_style = []
    who_move = get_who_move(game_id)
    if who_move == user_id:
        timer_style.append('background-color: #fff')
    else:
        timer_style.append('background-color: #A9A9A9')
    timer_style.extend(['border: 6px solid #ebdddd', 'border-radius: 10px 10px 10px 10px', 'padding: 5px;'])
    timer_style_st = ';'.join(timer_style) + ';'
    return timer_style_st


def is_winner_in_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    if game.winner == 0:
        return False
    else:
        return True


def get_just_winner(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    return game.winner


def add_user_to_players_in_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    game.players_in_game = game.players_in_game + ' ' + str(current_user.id)
    session.commit()
    session.close()


def remove_from_players_in_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    if len(game.players_in_game.split()) == 2:
        sp = game.players_in_game.split()
        sp.remove(str(current_user.id))
        game.players_in_game = sp[0]
    elif len(game.players_in_game.split()) == 1 and str(current_user.id) in game.players_in_game.split():
        session.delete(game)
    session.commit()
    session.close()


def delete_searching_game():
    session = db_session.create_session()
    games = session.query(Game).all()
    for game in games:
        if len(game.players_ids.split()) == 1 and str(current_user.id) in game.players_ids.split() and game.winner == 0:
            session.delete(game)
            session.commit()
            session.close()
            return 'success'
    return 'nothing'