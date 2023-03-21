from data import db_session
from data.users import User
from data.games import Game


def is_user_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return False
    return True


def is_user_in_game(user_id):
    session = db_session.create_session()
    games = session.query(Game).all()
    for game in games:
        if str(user_id) in game.players_ids.split():
            return True
    return False


def get_user(user_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    return {'user': user.to_dict()}


def delete_user(user_id):
    if not is_user_found(user_id):
        return {'error': 404}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.delete(user)
    session.commit()
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
    return {'success': 'OK'}


def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
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
    user.image_name = user.email
    user.set_password(args['password'])
    session.commit()
    return {'success': 'OK'}