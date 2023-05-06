from funcs.game_funcs import get_top_players
from data import db_session
db_session.global_init("db/main.db")

print(get_top_players(5))