from funcs.game_funcs import *
from funcs.user_funcs import *
from data import db_session
from flask import url_for, Flask

db_session.global_init("db/main.db")
print('<button style="background: transparent;border: none !important;" ' + 'onclick="' + "document.location='/';" + '">' + '<img src="../static/images/buttons/back_button.png" style="width: 100px;"></button>')