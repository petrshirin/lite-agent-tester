from telebot import types, TeleBot
from bot_logic.models import Student, Test, Answer, StudentTest, StudentAnswer, Question
from .lang import Lang
from .keyboards import Keyboards
from telebot.apihelper import ApiException
from typing import Union
from bot_logic.utils import \
    calculated_dict_to_array, calculate_question, \
    check_user_pay_status, check_user_status


class UserLogic:

    def __init__(self, bot: TeleBot, message: types.Message, user: Student):
        """
        :param bot: TeleBot object for working with telegram API
        :param message: Message object from user
        :param user: Student object, need for getting student info
        :return StudentLogic object
        """
        self.bot = bot
        self.message = message
        self.user = user
        self.language = Lang(self.user.language if self.user else "RU").select_current_lang()
        self.keyboards = Keyboards()

    def welcome(self):
        if not self.user:
            self.user = Student.objects.create(user_id=self.message.chat.id)
            self.send_common_message(self.language.need_register, None)
        self.send_common_message(self.language.welcome, None)
        if self.user.step < 10:
            self.send_common_message(self.language.register_fio, None)
            self.user.step = 1
            self.user.save()
            return 1
        else:
            self.main_menu()
        return self.user.step

    def register_user(self):
        if self.user.step == 1:
            self.user.step = self.get_user_fio()
        elif self.user.step == 2:
            self.user.step = self.get_user_agency()
        elif self.user.step == 3:
            self.user.step = self.get_user_city()
        self.user.save()

    def get_user_fio(self, next_status: int = 2):
        if not self.user:
            self.user = Student.objects.create(self.message.chat.id)
        self.user.FIO = self.message.text
        self.user.save()
        self.send_common_message(self.language.register_agency, None)
        return next_status

    def get_user_agency(self, next_status: int = 3):
        self.user.agency = self.message.text
        self.user.save()
        self.send_common_message(self.language.register_city, None)
        return next_status

    def get_user_city(self, next_status: int = 10):
        self.user.city = self.message.text
        self.user.save()
        self.main_menu()
        return next_status

    def send_common_message(self, text: str, markup: Union[types.InlineKeyboardMarkup, None]):
        try:
            self.bot.edit_message_text(
                text=text,
                chat_id=self.user.user_id,
                message_id=self.message.message_id,
                reply_markup=markup)
        except ApiException:
            self.bot.send_message(
                chat_id=self.user.user_id,
                text=text,
                reply_markup=markup)

    def main_menu(self):
        text = self.language.main_menu
        markup = self.keyboards.get_main_menu()
        self.send_common_message(text, markup)
        return self.user.step

    def class_menu(self, class_name="agent"):
        text = self.language.class_menu
        markup = self.keyboards.get_class_menu(0, class_name)
        self.send_common_message(text, markup)
        return self.user.step

    def start_theory(self, class_name: str, page: int, **kwargs):
        if not kwargs.get('returned'):
            if not self.check_checked_question(class_name, page):
                return self.user.step
        if class_name == "agent":
            check_user_pay_status(self, 1, self.agent_theory, page)()
        elif class_name == "broker":
            check_user_pay_status(self, 2, self.broker_theory, page)()

    def check_checked_question(self, class_name: str, page: int):
        answers = self.user.studentcondition.current_selected_answers.all()
        if page == 0:
            self.user.studentcondition.current_selected_answers.clear()
            self.user.studentcondition.save()
            return True
        elif len(answers):
            is_checked = True
            if answers[0].question.multi_answer:
                all_count_question = answers[0].question.answer_set.filter(is_right=True).count()
            else:
                all_count_question = 1
            if len(answers) != all_count_question:
                self.start_theory(class_name, page - 1, returned=True)
                is_checked = False
            else:
                for answer in answers:
                    if not answer.is_right:
                        self.user.studentcondition.current_selected_answers.clear()
                        self.user.studentcondition.save()
                        self.start_theory(class_name, page-1, returned=True)
                        is_checked = False
                        return is_checked
            self.user.studentcondition.current_selected_answers.clear()
            self.user.studentcondition.save()
            return is_checked
        return False

    def agent_theory(self, page: int):
        test = Test.objects.filter(pk=1).first()
        if not test:
            self.bot.send_message(self.user.user_id, self.language.test_not_found)
            return check_user_status(self, self.main_menu)()
        questions = test.question_set.all()
        if len(questions) == page:
            return self.main_menu()
        question = questions[page]
        text = self.language.theory_wrapper.format(question.category, question.paragraph)
        markup = self.keyboards.generate_keyboard_for_theory_block(page, 'agent')
        self.send_common_message(text, markup)
        return self.user.step

    def checked_question(self, class_name: str, page: int):
        test = None
        if class_name == 'agent':
            test = Test.objects.filter(pk=1).first()
        elif class_name == 'broker':
            test = Test.objects.filter(pk=2).first()
        if not test:
            self.bot.send_message(self.user.user_id, self.language.test_not_found)
            return check_user_status(self, self.main_menu)()
        question = test.question_set.all()[page]
        text = self.language.question_wrapper.format(page + 1, question.text)
        markup = self.keyboards.generate_keyboard_for_theory_question(
            class_name,
            self.user,
            question,
            page,
            test.pk)
        self.send_common_message(text, markup)
        return self.user.step

    def broker_theory(self, page: int):
        test = Test.objects.filter(pk=2).first()
        if not test:
            self.bot.send_message(self.user.user_id, self.language.test_not_found)
            return check_user_status(self, self.main_menu)()

        questions = test.question_set.all()
        if len(questions) == page:
            return self.main_menu()

        question = questions[[page]]
        text = self.language.theory_wrapper.format(question.category, question.paragraph)
        markup = self.keyboards.generate_keyboard_for_theory_block(page, 'broker')
        self.send_common_message(text, markup)
        return self.user.step

    def start_test(self, name: str):
        if name == "agent":
            test = Test.objects.filter(pk=1).first()
            StudentTest.objects.create(test=test, student=self.user)
            return self.agent_test(0)
        elif name == "broker":
            test = Test.objects.filter(pk=2).first()
            StudentTest.objects.create(test=test, student=self.user)
            return self.broker_test(0)

    def next_question(self, test_num: int, question_num: int):
        if question_num:
            if not self.save_answer():
                return 10
        if test_num == 1:
            return self.agent_test(question_num)
        elif test_num == 2:
            return self.broker_test(question_num)

    def broker_test(self, question_num=0):
        test = Test.objects.filter(pk=2).first()
        if not test:
            self.bot.send_message(self.user.user_id, self.language.test_not_found)
            return check_user_status(self, self.main_menu)()

        questions = test.question_set.all()
        if question_num == len(questions) - 1:
            return self.complete_test()
        else:
            question = questions[question_num]
        text = self.language.question_wrapper.format(question_num, question.text)
        markup = self.keyboards.generate_keyboard_for_test(self.user, question, question_num, 2)

        self.send_common_message(text, markup)
        return self.user.step

    def agent_test(self, question_num=0):
        test = Test.objects.filter(pk=1).first()
        if not test:
            self.bot.send_message(self.user.user_id, self.language.test_not_found)
            return check_user_status(self, self.main_menu)()

        questions = test.question_set.all()
        if question_num == len(questions):
            return self.complete_test()
        else:
            question = questions[question_num]
        markup = self.keyboards.generate_keyboard_for_test(self.user, question, question_num, 1)
        text = self.language.question_wrapper.format(question_num + 1, question.text)

        self.send_common_message(text, markup)

    def clear_selected_answer(self, clear_place: str, test_num: int, num: int):
        self.user.studentcondition.current_selected_answers.clear()
        if test_num == 1:
            if clear_place == "test":
                return self.agent_test(num)
            else:
                return self.checked_question('agent', num)
        elif test_num == 2:
            if clear_place == "test":
                return self.broker_test(num)
            else:
                return self.checked_question('broker', num)

    def select_answer(self, select_place: str, test_num: int, num: int, answer_id: int):
        answer = Answer.objects.filter(pk=answer_id).first()
        if answer:
            self.user.studentcondition.current_selected_answers.add(answer)
            self.user.studentcondition.save()
        if test_num == 1:
            if select_place == 'test':
                return self.agent_test(num)
            else:
                return self.checked_question('agent', num)
        elif test_num == 2:
            if select_place == 'test':
                return self.broker_test(num)
            else:
                return self.checked_question('broker', num)

    def save_answer(self):
        user_selected_answers = self.user.studentcondition.current_selected_answers.all()
        question = user_selected_answers[0].question
        try:
            student_answer = StudentAnswer.objects.create(
                student=self.user,
                question=question,
                test=StudentTest.objects.filter(student=self.user, closed=False).first())
        except Exception:
            text = self.language.student_test_not_found
            self.send_common_message(text, None)
            check_user_status(self, self.main_menu)()
            self.user.studentcondition.current_selected_answers.clear()
            self.user.studentcondition.save()
            return False
        for selected_answer in user_selected_answers:
            student_answer.answers.add(selected_answer)
        student_answer.save()
        self.user.studentcondition.current_selected_answers.clear()
        self.user.studentcondition.save()
        return True

    def complete_test(self):
        student_test = StudentTest.objects.filter(student=self.user, closed=False).first()
        if not student_test:
            text = self.language.test_not_found
            self.send_common_message(text, None)
            return

        student_test.closed = True
        questions = student_test.test.question_set.all()
        errors = {}
        all_points = student_test.test.question_set.count()
        true_point = 0
        for question in questions:
            point, error = calculate_question(student_test, question)
            if point:
                true_point += 1
            else:
                if error:
                    if errors.get(error):
                        errors[error] += 1
                    else:
                        errors[error] = 1

        student_test.save()
        text = self.language.test_info.format(true_point, all_points, "{}".format(calculated_dict_to_array(errors)))
        self.send_common_message(text, None)
        return self.user.step
