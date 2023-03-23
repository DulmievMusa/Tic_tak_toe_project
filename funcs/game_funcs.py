from data import db_session
from data.games import Game
from flask import session
from funcs.user_funcs import *


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
        who_move=0,
        matrix='000000000',
        waitcount=0,
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
    session['playing'] = True


def is_game_full(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    if len(game.players_ids.split()) == 2:
        return True
    return False