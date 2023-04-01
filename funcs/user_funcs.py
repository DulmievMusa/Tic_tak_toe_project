from data import db_session
from data.users import User
from data.games import Game
from random import randint
from flask import redirect, session
from flask_login import current_user


def is_user_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    if not user:
        return False
    return True


def get_opponent_idik(game_id, user_id):
    session = db_session.create_session()
    game = session.query(Game).get(game_id)
    session.close()
    players = game.players_ids.split()
    players.remove(str(user_id))
    return players[0]


def is_user_in_game(user_id):
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if str(user_id) in game.players_ids.split() and game.winner == 0:
            return True
    return False


def get_game_where_user_play(user_id):
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if (str(user_id) in game.players_ids.split() and game.winner == 0):
            return game.id
    return None


def get_user(user_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    return {'user': user.to_dict()}


def get_user_short(user_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    return {'user': user.to_dict(only=('name', 'rating', 'country'))}


def delete_user(user_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.delete(user)
    session.commit()
    session.close()
    return {'success': 'OK'}


def edit_user(user_id, args):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    user.name = args.get('name', user.name)
    user.rating = args.get('rating', user.rating)
    user.country = args.get('country', user.country)
    user.email = args.get('email', user.email)
    user.image_name = args.get('image_name', user.image_name)
    user.set_password(args.get('password', user.hashed_password))
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    session.close()
    return {'users': [item.to_dict() for item in users]}


def add_user(args):
    session = db_session.create_session()
    user = User(
        name=args['name'],
        rating=args['rating'],
        country=args['country'],
        email=args['email'],
    )
    session.add(user)
    user.set_password(args['password'])
    session.commit()
    session.close()
    return {'success': 'OK'}


def get_short_user_list(user_id):
    user = get_user_short(user_id)['user']
    sp = []
    sp.append(user['name'])
    sp.append(user['country'])
    sp.append((user['rating']))
    return sp


def get_where_user_sitting(user_id):
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if (str(user_id) in game.players_ids.split() and game.winner == 0):
            return game.id
    return None


def get_how_plus(user_id, winner):
    if user_id == winner:
        return randint(19, 21)
    else:
        return randint(-11, -9)


def increase_rating(user_id, winner_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    how_plus = get_how_plus(user_id, winner_id)
    user.rating = max(user.rating + get_how_plus(user_id, winner_id), 0)
    session.commit()
    session.close()


def get_rating_pluses(game_id):
    opponent_plus = get_user(get_opponent_idik(game_id, current_user.id))['user']['rating'] - session[
        'old_opponent_rating']
    if opponent_plus > 0:
        opponent_plus = '+ ' + str(opponent_plus)
    elif opponent_plus < 0:
        opponent_plus = '- ' + str(abs(opponent_plus))
    user_plus = get_user(current_user.id)['user']['rating'] - session[
        'old_user_rating']
    if user_plus > 0:
        user_plus = '+ ' + str(user_plus)
    elif user_plus < 0:
        user_plus = '- ' + str(abs(user_plus))
    return (opponent_plus, user_plus)


def get_game_where_user_played(user_id):
    session = db_session.create_session()
    games = session.query(Game).all()
    session.close()
    for game in games:
        if (str(user_id) in game.players_ids.split() and game.winner != 0):
            return game.id
    return None