from telebot import types
from bot_logic.models import Question, Student


class ButtonData:
    def __init__(self, name: str, data: str):
        self.name = name
        self.data = data

    def to_telegram(self, **kwargs):
        if isinstance(kwargs.get('name', []), list) or isinstance(kwargs.get('data', []), list):
            return types.InlineKeyboardButton(self.name.format(*kwargs.get('name', [""])),
                                              callback_data=self.data.format(*kwargs.get('data', [""])))
        else:
            return types.InlineKeyboardButton(self.name.format(*kwargs.get('name', [""])),
                                              callback_data=self.data.format(*kwargs.get('data', [""])))


class Keyboards:
    agent_start = ButtonData("Агенту", "menu?agent/")
    broker_start = ButtonData("Брокеру", "menu?broker/")
    theory = ButtonData("Теория", "theory?{}/{}/")
    agent_test = ButtonData("Пройти тест", "test?agent")
    broker_test = ButtonData("Пройти тест", "test?broker")
    back = ButtonData("Назад", "{}")
    next_question = ButtonData('Следующий вопрос', "question?{}/{}/")
    answer_option = ButtonData("{}", "answer?{}/{}/{}/{}/")
    complete_test = ButtonData("Завершить тест", "complete_test")
    clear_selected_answer = ButtonData("Отчистить ответы", "clear_selected_answers?{}/{}/{}")
    checked_question = ButtonData("Проверочный вопрос", "checkedquestion?{}/{}/")
    checked_answer = ButtonData("Следующий раздел", "theory?{}/{}/")

    def __init__(self, lang='RU'):
        self.lang = lang

    def select_current_lang(self):
        if self.lang == 'RU':
            return KeyboardsRu()

    def get_main_menu(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(self.agent_start.to_telegram(),
                     self.broker_start.to_telegram())
        return keyboard

    def get_class_menu(self,  page: int, class_name: str = "agent") -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(self.theory.to_telegram(data=[class_name, page]),
                     self.agent_test.to_telegram())
        return keyboard

    def generate_keyboard_for_test(self, user: Student, question: Question, question_num: int, test_num: int) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for answer in question.answer_set.all():
            smile = "✅" if user.studentcondition.current_selected_answers.filter(pk=answer.pk).all() else ""
            keyboard.add(self.answer_option.to_telegram(name=[f"{smile}{answer.text}"], data=['test', test_num, question_num, answer.pk]))
        keyboard.add(self.complete_test.to_telegram(),
                     self.clear_selected_answer.to_telegram(data=['test', test_num, question_num]),
                     self.next_question.to_telegram(data=[test_num, question_num + 1]))
        return keyboard

    def generate_keyboard_for_theory_block(self, page: int, class_name="agent"):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        if class_name == 'agent':
            back = self.agent_start.to_telegram(data=[class_name, page - 1])
        elif class_name == 'broker':
            back = self.broker_start.to_telegram(data=[class_name, page - 1])
        else:
            return keyboard
        keyboard.add(
            back,
            self.checked_question.to_telegram(data=[class_name, page])
        )
        return keyboard

    def generate_keyboard_for_theory_question(self, class_name: str, user: Student, question: Question, page: int, test_num: int):
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for answer in question.answer_set.all():
            smile = "✅" if user.studentcondition.current_selected_answers.filter(pk=answer.pk).all() else ""
            keyboard.add(self.answer_option.to_telegram(name=[f"{smile}{answer.text}"], data=['theory', test_num, page, answer.pk]))

        if class_name == 'agent':
            back = self.agent_start.to_telegram(data=[class_name, page - 1])
        elif class_name == 'broker':
            back = self.broker_start.to_telegram(data=[class_name, page - 1])
        else:
            return keyboard
        keyboard.add(
            back,
            self.clear_selected_answer.to_telegram(data=['theory', test_num, page]),
            self.checked_answer.to_telegram(data=[class_name, page+1])
            )
        return keyboard


class KeyboardsRu(Keyboards):

    def __init__(self):
        super().__init__()



