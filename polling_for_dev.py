import django

django.setup()

from bot_logic.views import *
from bot_logic.utils import load_data_from_csv, load_data_to_db


if __name__ == '__main__':
    print('start')
    while True:
        try:
            bot.polling(none_stop=True)
        except ConnectionError as e:
            print(e)
            continue
