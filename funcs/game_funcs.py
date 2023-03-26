from data import db_session
from data.games import Game
from flask import session, url_for
from funcs.user_funcs import *
from random import choice


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
        winner=0)
    session.add(game)
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_free_game_id():
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if len(game.players_ids.split()) == 1:
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
            and get_game_where_user_play(user_id) is None:
        create_game(user_id)
        new_game_id = get_game_where_user_play(user_id)
        session['game_id'] = new_game_id
    else:
        if not is_user_in_game(user_id):
            free_game_id = get_free_game_id()
            session['game_id'] = free_game_id
            add_user_id_to_game(free_game_id, user_id)
            opponent_id = get_opponent_id(free_game_id, user_id)
            who_move_id = choice_who_move(user_id, opponent_id)
            set_who_move(free_game_id, who_move_id)

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


def to_images_matrix(matrix):
    mat = []
    for row in matrix:
        sp = []
        for elem in row:
            if elem == '0':
                sp.append(url_for('static', filename='images/game_sprites/circle.png'))
            elif elem == 'X':
                sp.append(url_for('static', filename='images/game_sprites/cross.png'))
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
    session.commit()
    session.close()