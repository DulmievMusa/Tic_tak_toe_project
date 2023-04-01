from funcs.game_funcs import *
from funcs.user_funcs import *
from data import db_session
from flask import url_for, Flask
from funcs.different_funcs import is_lat_letters_all

print(is_lat_letters_all('Gogland'))