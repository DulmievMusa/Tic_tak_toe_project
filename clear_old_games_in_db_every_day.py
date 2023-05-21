from data import db_session
from data.games import Game
from datetime import datetime
import schedule
db_session.global_init("db/main.db")


def clear_games_db():
    session = db_session.create_session()
    games = session.query(Game).all()
    for game in games:
        date_delta = datetime.now() - game.last_time
        if date_delta.days >= 2 and game.winner != 0:
            session.delete(game)
    session.commit()
    session.close()


schedule.every().day.at("00:00").do(clear_games_db)
while True:
    schedule.run_pending()