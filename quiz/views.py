from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Question, QuizSession
import json


def start_quiz(request):
    return render(request, 'quiz/start.html')


def begin_quiz(request):
    all_questions = list(Question.objects.all().order_by('question_number').values_list('id', flat=True))

    if len(all_questions) < 50:
        return JsonResponse({'error': 'Not enough questions in database'}, status=400)

    selected_questions = all_questions[:50]

    quiz_session = QuizSession.objects.create()
    quiz_session.set_selected_questions(selected_questions)
    quiz_session.save()

    request.session['quiz_session_id'] = quiz_session.id

    return redirect('quiz_question', question_index=0)


def quiz_question(request, question_index):
    quiz_session_id = request.session.get('quiz_session_id')
    
    if not quiz_session_id:
        return redirect('start_quiz')
    
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    
    if quiz_session.is_completed:
        return redirect('quiz_results')
    
    selected_questions = quiz_session.get_selected_questions()
    
    if question_index < 0 or question_index >= len(selected_questions):
        return redirect('quiz_question', question_index=0)
    
    question_id = selected_questions[question_index]
    question = get_object_or_404(Question, id=question_id)
    
    user_answers = quiz_session.get_user_answers()
    selected_answer = user_answers.get(str(question.id), '')
    
    time_elapsed = (timezone.now() - quiz_session.start_time).total_seconds()
    time_remaining = max(0, 3600 - time_elapsed)
    
    if time_remaining <= 0:
        quiz_session.end_time = timezone.now()
        quiz_session.is_completed = True
        quiz_session.calculate_score()
        quiz_session.save()
        return redirect('quiz_results')
    
    context = {
        'question': question,
        'question_index': question_index,
        'total_questions': len(selected_questions),
        'selected_answer': selected_answer,
        'time_remaining': int(time_remaining),
        'quiz_session_id': quiz_session.id,
    }
    
    return render(request, 'quiz/question.html', context)


def save_answer(request):
    if request.method == 'POST':
        quiz_session_id = request.session.get('quiz_session_id')
        
        if not quiz_session_id:
            return JsonResponse({'error': 'No active quiz session'}, status=400)
        
        quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
        
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if question_id and answer:
            quiz_session.set_user_answer(question_id, answer)
            quiz_session.save()
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def submit_quiz(request):
    quiz_session_id = request.session.get('quiz_session_id')
    
    if not quiz_session_id:
        return redirect('start_quiz')
    
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    
    quiz_session.end_time = timezone.now()
    quiz_session.is_completed = True
    quiz_session.calculate_score()
    quiz_session.save()
    
    return redirect('quiz_results')


def quiz_results(request):
    quiz_session_id = request.session.get('quiz_session_id')
    
    if not quiz_session_id:
        return redirect('start_quiz')
    
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    
    if not quiz_session.is_completed:
        return redirect('quiz_question', question_index=0)
    
    selected_questions = quiz_session.get_selected_questions()
    questions = Question.objects.filter(id__in=selected_questions).order_by('question_number')
    user_answers = quiz_session.get_user_answers()

    results = []
    for question in questions:
        user_answer = user_answers.get(str(question.id), '')
        is_correct = user_answer == question.correct_option
        
        results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    
    context = {
        'quiz_session': quiz_session,
        'total_questions': len(selected_questions),
        'score': quiz_session.score,
        'percentage': (quiz_session.score / len(selected_questions)) * 100,
    }
    
    return render(request, 'quiz/results.html', context)


def quiz_explanation(request):
    quiz_session_id = request.session.get('quiz_session_id')
    
    if not quiz_session_id:
        return redirect('start_quiz')
    
    quiz_session = get_object_or_404(QuizSession, id=quiz_session_id)
    
    if not quiz_session.is_completed:
        return redirect('quiz_question', question_index=0)
    
    selected_questions = quiz_session.get_selected_questions()
    questions = Question.objects.filter(id__in=selected_questions).order_by('question_number')
    user_answers = quiz_session.get_user_answers()

    wrong_questions = []
    for question in questions:
        user_answer = user_answers.get(str(question.id), '')
        is_correct = user_answer == question.correct_option
        
        if not is_correct:
            wrong_questions.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': question.correct_option,
            })
    
    context = {
        'wrong_questions': wrong_questions,
        'quiz_session': quiz_session,
    }
    
    return render(request, 'quiz/explanation.html', context)
