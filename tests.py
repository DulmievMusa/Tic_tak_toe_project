from funcs.game_funcs import *
from funcs.user_funcs import *
from data import db_session
from flask import url_for, Flask
from funcs.different_funcs import is_lat_letters_all

print('<button style="padding: 10px;font-family: Arial, Helvetica, sans-serif;border: 6px solid #4773a6;border-radius: 10px 10px 10px 10px;" ' + 'onclick="' + "document.location='/';" + '">' + '<h1>Back</h1></button>')