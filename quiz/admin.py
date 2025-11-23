from django.contrib import admin
from .models import Question, QuizSession


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_number', 'question_text', 'correct_option']
    search_fields = ['question_text']
    list_filter = ['correct_option']


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_time', 'end_time', 'score', 'is_completed']
    list_filter = ['is_completed', 'start_time']
    readonly_fields = ['start_time', 'end_time', 'score']
