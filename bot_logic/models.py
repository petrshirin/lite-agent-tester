from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


# Create your models here.


class Test(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['-pk']


class Question(models.Model):
    text = models.TextField()
    category = models.CharField(max_length=255, default="Без категории", blank=True)
    paragraph = models.TextField(blank=True)
    multi_answer = models.BooleanField(default=False)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    class Meta:
        ordering = ['pk']


class Answer(models.Model):
    text = models.TextField()
    is_right = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pk']


class Student(models.Model):
    user_id = models.IntegerField(default=0)
    language = models.CharField(max_length=5, default='RU')
    step = models.IntegerField(default=0)

    FIO = models.CharField(max_length=500, default=None, null=True, blank=True)
    agency = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)


class StudentCondition(models.Model):
    tests = models.ManyToManyField(Test, related_name='tests', blank=True)
    current_test = models.ForeignKey(
        Test,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='current_test',
        blank=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, blank=True)
    current_selected_answers = models.ManyToManyField(Answer, blank=True)


class StudentTest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    date_start = models.DateTimeField(default=now)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Answer)
    test = models.ForeignKey(StudentTest, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pk']


@receiver(post_save, sender=Student)
def create_student_additional_tables(sender: Student, instance: Student, created: bool, **kwargs):
    if created:
        StudentCondition.objects.create(student=instance)
