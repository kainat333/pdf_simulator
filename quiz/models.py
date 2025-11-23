from django.db import models
import json


class Question(models.Model):
    question_number = models.IntegerField(unique=True)
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField()

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Question {self.question_number}"


class QuizSession(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    selected_questions = models.TextField()
    user_answers = models.TextField(default='{}')
    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    current_question_index = models.IntegerField(default=0)

    def set_selected_questions(self, questions_list):
        self.selected_questions = json.dumps(questions_list)

    def get_selected_questions(self):
        return json.loads(self.selected_questions)

    def set_user_answer(self, question_id, answer):
        answers = json.loads(self.user_answers)
        answers[str(question_id)] = answer
        self.user_answers = json.dumps(answers)

    def get_user_answers(self):
        return json.loads(self.user_answers)

    def calculate_score(self):
        answers = self.get_user_answers()
        selected_questions = self.get_selected_questions()
        questions = Question.objects.filter(id__in=selected_questions)
        
        correct_count = 0
        for question in questions:
            user_answer = answers.get(str(question.id))
            if user_answer == question.correct_option:
                correct_count += 1
        
        self.score = correct_count
        return correct_count

    def __str__(self):
        return f"Quiz Session {self.id} - Score: {self.score}/50"
