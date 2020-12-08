from bot_logic.models import StudentTest, StudentAnswer, Question, Test, Answer
from typing import List, Dict


def calculated_dict_to_array(data: dict) -> str:
    result = [""]
    for key, value in data.items():
        result.append(f"{key}: {value}\n")
    return "".join(result)


def calculate_question(student_test: StudentTest, question: Question):
    student_answer = StudentAnswer.objects.filter(test=student_test, question=question).first()
    if not student_answer:
        return 0, None
    error = None
    if question.multi_answer:
        is_right = True
        for answer in student_answer.answers.all():
            if answer not in question.answer_set.filter(is_right=True).all():
                is_right = False
                error = question.category
                break
    else:
        is_right = True
        for answer in student_answer.answers.all():
            if answer not in question.answer_set.filter(is_right=True).all():
                is_right = False
                error = question.category
                break

    return is_right, error


# pay middleware
def check_user_pay_status(self, test_num: int, func, page: int):

    def wrapper():
        if not Test.objects.all()[test_num] in self.user.studentcondition.tests.all():
            self.bot.send_message(self.user.user_id, self.language.invalid_pay_status)
            return 1
        else:
            result = func(page)
        return result

    return wrapper


# register middleware
def check_user_status(self, func):

    def wrapper():
        if self.user and self.user.step >= 10:
            func()
        else:
            self.user.step = 1
            self.user.save()
            self.register_user()

    return wrapper


def load_data_from_csv():
    with open('data_agent.csv', 'r', encoding='utf-8') as f:
        result = []
        category = None
        rows = f.readlines()
        text_paragraph = ""
        text_question = ""
        answers = []
        number_of_question = None
        for i in range(len(rows)):
            rows[i] = rows[i][:-1]
            data = rows[i].split(';')
            try:
                if data[1]:
                    category = data[1]

                if data[0]:
                    number_of_question = data[0]
                    text_paragraph += f"{data[2]}\n"
                    text_question += f"{data[3]}\n"
                    i += 1
                    data = rows[i].split(';')

                    while not data[0]:
                        text_paragraph += f"{data[2]}\n"
                        text_question += f"{data[3]}\n"
                        if not answers:
                            for answer in data[5:]:
                                if answer and answer != '\n':
                                    if answer[0] == '1':
                                        answers.append({'text': answer[1:], "is_right": True})
                                    else:
                                        answers.append({'text': answer, "is_right": False})
                        i += 1
                        data = rows[i].split(';')

                    i -= 1
                    result.append({
                        "category": category,
                        "paragraph": text_paragraph,
                        "question": text_question,
                        "answers": answers.copy()
                    })
                    text_paragraph = ""
                    text_question = ""
                    answers.clear()
            except IndexError:
                text_paragraph = ""
                text_question = ""
                answers.clear()
                print(number_of_question)
                continue
    return result


def load_data_to_db(result: List[Dict]):
    # Question.objects.all().delete()
    for row in result:
        is_multi = False
        count_right_questions = 0
        for answer in row['answers']:
            if answer['is_right']:
                count_right_questions += 1

        if count_right_questions > 1:
            is_multi = True

        question = Question.objects.create(
            category=row['category'],
            text=row['question'],
            paragraph=row['paragraph'],
            multi_answer=is_multi,
            test_id=1
        )
        for dict_answer in row['answers']:
            Answer.objects.create(
                text=dict_answer['text'],
                is_right=dict_answer['is_right'],
                question=question
            )


def generate_answers_in_message(answers: List[Answer]):
    text = ""
    i = 1
    for answer in answers:
        text += f"{i} - {answer.text}\n"
        i += 1
    return text

