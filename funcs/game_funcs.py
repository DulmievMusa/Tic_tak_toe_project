from data import db_session
from data.games import Game


def is_game_found(game_id):
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    if not game:
        return False
    return True


def get_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    return {'game': game.to_dict()}


def delete_game(game_id):
    if not is_game_found(game_id):
        return {'error': 404}
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.delete(game)
    session.commit()
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
    return {'success': 'OK'}


def get_games():
    session = db_session.create_session()
    games = session.query(Game).all()
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
    return {'success': 'OK'}


def get_free_game_id():
    session = db_session.create_session()
    games = session.query(Game).all()
    for game in games:
        if len(game.players_ids.split()) == 1:
            return game.id
    return None