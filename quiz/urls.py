from django.urls import path
from . import views

urlpatterns = [
    path('', views.start_quiz, name='start_quiz'),
    path('begin/', views.begin_quiz, name='begin_quiz'),
    path('question/<int:question_index>/', views.quiz_question, name='quiz_question'),
    path('save-answer/', views.save_answer, name='save_answer'),
    path('submit/', views.submit_quiz, name='submit_quiz'),
    path('results/', views.quiz_results, name='quiz_results'),
    path('explanation/', views.quiz_explanation, name='quiz_explanation'),
]
