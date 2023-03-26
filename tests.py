from funcs.game_funcs import *
from funcs.user_funcs import *
from data import db_session
from flask import url_for, Flask

db_session.global_init("db/main.db")
print(get_game(1))