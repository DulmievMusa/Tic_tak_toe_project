import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'  # game_id, players_ids, who_move, matrix, waitcount, start_time, winner

    game_id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    players_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    who_move = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    matrix = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    waitcount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    winner = sqlalchemy.Column(sqlalchemy.String, nullable=True)