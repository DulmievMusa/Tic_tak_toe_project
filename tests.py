from funcs.game_funcs import *
from funcs.user_funcs import *
from data import db_session
db_session.global_init("db/main.db")
print(get_user(10))
