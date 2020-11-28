from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Question)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category', 'test', 'multi_answer')
    list_filter = ('test', 'category')


@admin.register(Answer)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'is_right', 'question')
    list_filter = ('question__test',)


admin.site.register(Student)
admin.site.register(StudentCondition)
admin.site.register(StudentAnswer)
admin.site.register(StudentTest)
admin.site.register(Test)
