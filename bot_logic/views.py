from telebot import TeleBot, types
import json
from django.http import HttpResponse
import logging
from django.conf import settings
from .models import *
from .bot_logic.user_controllers import UserLogic
from bot_logic.payload_router import Router

LOG = logging.getLogger(__name__)
bot = TeleBot(settings.TELEGRAM_TOKEN, threaded=False)


def get_web_hook(request):

    json_data = json.loads(request.body)
    global bot
    request_body_dict = json_data
    update = types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return HttpResponse('ok', status=200)


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    user = Student.objects.filter(user_id=message.chat.id).first()
    action = UserLogic(bot, message, user)
    action.welcome()


@bot.message_handler(content_types=['text'])
def text_logic(message: types.Message):
    user = Student.objects.filter(user_id=message.chat.id).first()
    action = UserLogic(bot, message, user)
    action.register_user()


@bot.callback_query_handler(func=lambda c: True)
def inline_logic(c):
    print(c.data)
    user = Student.objects.get(user_id=c.message.chat.id)
    action = UserLogic(bot, c.message, user)
    router = Router()
    router.add_route('menu?<str:class_name>/', action.class_menu)
    router.add_route('theory?<str:class_name>/<int:page>/', action.start_theory)
    router.add_route('test?<str:name>/', action.start_test)
    router.add_route('question?<int:test_num>/<int:question_num>/', action.next_question)
    router.add_route('answer?<str:select_place>/<int:test_num>/<int:num>/<int:answer_id>/', action.select_answer)
    router.add_route('complete_test', action.complete_test, parsed=False)
    router.add_route('checkedquestion?<str:class_name>/<int:page>/', action.checked_question)
    router.add_route('clear_selected_answers?<str:clear_place>/<int:test_num>/<int:num>/', action.clear_selected_answer)
    router.find_route(c.data)
