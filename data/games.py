import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    players_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    who_move_first = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    who_move = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    matrix = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_time = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    winner = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    players_in_game = sqlalchemy.Column(sqlalchemy.String, nullable=True)