

class Lang:
    welcome = """Вы находитесь в обучающем тренажере для подготовки к аттестации РГР.
    Вы можете пройти обучение, чтобы подготовиться к аттестации или пройти тестирование"""
    need_register = "Вам нужно зарегистрироваться!"
    main_menu = """Выберите, на кого вы хотите учиться:"""
    test_not_found = """Выбранный вами тест не найден, обратитесь к администратору бота"""
    invalid_pay_status = "Этот тест вы не оплатили, " \
                         "перейдите в окно оплаты или обратитесь к Админимстратору"
    question_wrapper = """Вопрос №{}

    {}
-------------
{}
-------------

    """
    class_menu = "Выберите, что вы хотите сделать:"
    student_test_not_found = "Тест, на который вы пытаетесь ответить не найден, начните заного"
    test_info = """Вы завершили тест
Колисчество баллов: {}/{}
{}

Ошибки по темам:
{} 
"""
    theory_wrapper = """{}

{}"""
    register_fio = """Введите ваше ФИО"""
    register_agency = """Введите название вашего агенства"""
    register_city = """Введите ваш город"""
    test_unavailable = """Этот тест недоступен, пройдите сперва тест Агента"""

    def __init__(self, lang='RU'):
        self.lang = lang

    def select_current_lang(self):
        if self.lang == 'RU':
            return LangRu()


class LangRu(Lang):

    def __init__(self):
        super().__init__()




