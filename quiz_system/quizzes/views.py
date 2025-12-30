from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Quiz, Question, Choice, Submission, Answer
from .serializers import (
    QuizListSerializer, QuizDetailSerializer, QuizSubmissionSerializer,
    SubmissionResultSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Quiz model
    - list: Get all active quizzes
    - retrieve: Get a specific quiz with all questions
    - submit: Submit answers for a quiz
    - check_submission: Check if email already submitted
    """
    queryset = Quiz.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizDetailSerializer

    @action(detail=True, methods=['post'], url_path='check-email')
    def check_email(self, request, pk=None):
        """Check if an email has already submitted this quiz"""
        quiz = self.get_object()
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response({'submitted': False})

        # Check if this email has already submitted this quiz
        existing_submission = Submission.objects.filter(
            quiz=quiz,
            email__iexact=email
        ).first()

        if existing_submission:
            return Response({
                'submitted': True,
                'message': 'You have already submitted this quiz.',
                'submitted_at': existing_submission.submitted_at
            })

        return Response({'submitted': False})

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit answers for a quiz and get results
        """
        quiz = self.get_object()
        serializer = QuizSubmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answers_data = serializer.validated_data['answers']
        name = serializer.validated_data['name']
        email = serializer.validated_data['email']

        # Check if this email has already submitted this quiz
        existing_submission = Submission.objects.filter(
            quiz=quiz,
            email__iexact=email
        ).first()

        if existing_submission:
            return Response(
                {'error': 'You have already submitted this quiz. Each person can only submit once.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create submission and answers in a transaction
        try:
            with transaction.atomic():
                submission = Submission.objects.create(
                    quiz=quiz,
                    name=name,
                    email=email,
                    score=0,
                    max_score=0
                )

                total_score = 0
                max_score = 0

                # Process each answer
                for answer_data in answers_data:
                    question_id = answer_data['question_id']

                    try:
                        question = Question.objects.get(id=question_id, quiz=quiz)
                    except Question.DoesNotExist:
                        return Response(
                            {'error': f'Question {question_id} not found in this quiz'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    max_score += question.points

                    # Determine if answer is correct based on question type
                    is_correct = False
                    choice = None
                    text_answer = None

                    if question.question_type in ['MCQ', 'TRUE_FALSE']:
                        choice_id = answer_data.get('choice_id')
                        if choice_id:
                            try:
                                choice = Choice.objects.get(id=choice_id, question=question)
                                is_correct = choice.is_correct
                            except Choice.DoesNotExist:
                                return Response(
                                    {'error': f'Choice {choice_id} not found for question {question_id}'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                    elif question.question_type == 'TEXT':
                        text_answer = answer_data.get('text_answer', '').strip()
                        # For text questions, check if there's a correct choice with matching text
                        correct_choices = question.choices.filter(is_correct=True)
                        if correct_choices.exists():
                            # Case-insensitive comparison with any correct answer
                            is_correct = any(
                                c.choice_text.strip().lower() == text_answer.lower()
                                for c in correct_choices
                            )

                    # Award points if correct
                    if is_correct:
                        total_score += question.points

                    # Create answer record
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        choice=choice,
                        text_answer=text_answer,
                        is_correct=is_correct
                    )

                # Update submission with final scores
                submission.score = total_score
                submission.max_score = max_score
                submission.save()

                # Return simple response without scores (admin can see scores in admin panel)
                return Response({
                    'id': str(submission.id),
                    'quiz_title': quiz.title,
                    'name': submission.name,
                    'email': submission.email,
                    'submitted_at': submission.submitted_at,
                    'message': 'Thank you for submitting! Your answers have been recorded and will be reviewed by the admin.'
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error processing submission: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing submission results
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionResultSerializer


# Template view for quiz taking page
def quiz_page(request, quiz_id):
    """Render the quiz taking page"""
    from django.views.decorators.csrf import ensure_csrf_cookie

    @ensure_csrf_cookie
    def view(request):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if quiz is active
        if not quiz.is_active:
            return render(request, 'error_page.html', {
                'error_title': 'Quiz Not Available',
                'error_message': 'This quiz is not currently active.'
            })

        # Check if URL has expired (24 hours)
        if quiz.is_url_expired:
            return render(request, 'error_page.html', {
                'error_title': 'Quiz URL Expired',
                'error_message': 'This quiz URL has expired. Quiz URLs are only valid for 24 hours after publication. Please contact the quiz administrator for a new link.'
            })

        return render(request, 'quiz_page.html', {'quiz': quiz})

    return view(request)


def index_page(request):
    """Render the home page with all quizzes"""
    return render(request, 'index.html')


def quiz_urls_admin(request):
    """Admin view to display all published quiz URLs"""
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def view(request):
        quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')
        return render(request, 'admin/quiz_urls.html', {'quizzes': quizzes})

    return view(request)


def get_question_api(request, question_id):
    """API endpoint to get question data for copying"""
    from django.http import JsonResponse
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def view(request):
        try:
            question = Question.objects.get(pk=question_id)
            return JsonResponse({
                'id': str(question.pk),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'points': question.points,
            })
        except Question.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

    return view(request)


def get_all_questions_api(request):
    """API endpoint to get all questions for dropdown"""
    from django.http import JsonResponse
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def view(request):
        questions = Question.objects.select_related('quiz').order_by('-created_at')[:50]
        data = []
        for q in questions:
            label = f"{q.question_text[:60]}..." if len(q.question_text) > 60 else q.question_text
            data.append({
                'id': str(q.pk),
                'label': f"{label} (Quiz: {q.quiz.title})",
                'question_text': q.question_text,
                'question_type': q.question_type,
                'points': q.points,
            })
        return JsonResponse({'questions': data})

    return view(request)



