"""
Management command to create a complete example quiz with questions and choices.
This helps you understand the correct structure.

Usage:
    python manage.py create_example_quiz
    python manage.py create_example_quiz --title "My Quiz"
"""

from django.core.management.base import BaseCommand
from quizzes.models import Quiz, Question, Choice
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create a complete example quiz with questions and choices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--title',
            type=str,
            default='Example Quiz',
            help='Title of the quiz to create',
        )

    def handle(self, *args, **options):
        title = options['title']

        self.stdout.write(self.style.SUCCESS(f'\nCreating quiz: "{title}"\n'))

        # Create the quiz
        quiz = Quiz.objects.create(
            title=title,
            description='This is an example quiz to demonstrate the correct structure',
            is_active=True,
            published_at=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS(f'Quiz created: {quiz.title}'))
        self.stdout.write(f'   ID: {quiz.id}\n')

        # Question 1: Python basics
        q1 = Question.objects.create(
            quiz=quiz,
            question_text='What is Python primarily used for?',
            question_type='MCQ',
            points=1,
            order=0
        )
        
        Choice.objects.create(question=q1, choice_text='Video editing', is_correct=False, order=0)
        Choice.objects.create(question=q1, choice_text='Programming and software development', is_correct=True, order=1)
        Choice.objects.create(question=q1, choice_text='Graphic design', is_correct=False, order=2)
        Choice.objects.create(question=q1, choice_text='Hardware manufacturing', is_correct=False, order=3)
        
        self.stdout.write(self.style.SUCCESS(f'Question 1 added with 4 choices'))

        # Question 2: Django
        q2 = Question.objects.create(
            quiz=quiz,
            question_text='Django is a framework for which programming language?',
            question_type='MCQ',
            points=1,
            order=1
        )
        
        Choice.objects.create(question=q2, choice_text='JavaScript', is_correct=False, order=0)
        Choice.objects.create(question=q2, choice_text='Python', is_correct=True, order=1)
        Choice.objects.create(question=q2, choice_text='Java', is_correct=False, order=2)
        Choice.objects.create(question=q2, choice_text='Ruby', is_correct=False, order=3)
        
        self.stdout.write(self.style.SUCCESS(f'Question 2 added with 4 choices'))

        # Question 3: True/False
        q3 = Question.objects.create(
            quiz=quiz,
            question_text='Is Python an interpreted language?',
            question_type='TRUE_FALSE',
            points=1,
            order=2
        )
        
        Choice.objects.create(question=q3, choice_text='True', is_correct=True, order=0)
        Choice.objects.create(question=q3, choice_text='False', is_correct=False, order=1)
        
        self.stdout.write(self.style.SUCCESS(f'Question 3 added (True/False)'))

        # Question 4: Lists
        q4 = Question.objects.create(
            quiz=quiz,
            question_text='Which of the following is the correct way to create a list in Python?',
            question_type='MCQ',
            points=1,
            order=3
        )
        
        Choice.objects.create(question=q4, choice_text='list = (1, 2, 3)', is_correct=False, order=0)
        Choice.objects.create(question=q4, choice_text='list = [1, 2, 3]', is_correct=True, order=1)
        Choice.objects.create(question=q4, choice_text='list = {1, 2, 3}', is_correct=False, order=2)
        Choice.objects.create(question=q4, choice_text='list = <1, 2, 3>', is_correct=False, order=3)
        
        self.stdout.write(self.style.SUCCESS(f'Question 4 added with 4 choices'))

        # Question 5: Variables
        q5 = Question.objects.create(
            quiz=quiz,
            question_text='In Python, do you need to declare variable types explicitly?',
            question_type='TRUE_FALSE',
            points=1,
            order=4
        )
        
        Choice.objects.create(question=q5, choice_text='True', is_correct=False, order=0)
        Choice.objects.create(question=q5, choice_text='False', is_correct=True, order=1)
        
        self.stdout.write(self.style.SUCCESS(f'Question 5 added (True/False)\n'))

        # Summary
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS(f'\nQuiz "{quiz.title}" created successfully!\n'))
        self.stdout.write(f'   Total questions: {quiz.question_count}')
        self.stdout.write(f'   Total points: {quiz.total_points}')
        self.stdout.write(f'   Quiz ID: {quiz.id}\n')
        
        # Public URL
        self.stdout.write(self.style.SUCCESS('Public Quiz URL:'))
        self.stdout.write(f'   /quiz/{quiz.id}/')
        self.stdout.write(f'   (Access via: http://localhost:8000/quiz/{quiz.id}/ or http://127.0.0.1:8000/quiz/{quiz.id}/)\n')
        
        # Admin URL
        self.stdout.write(self.style.SUCCESS('Admin Edit URL:'))
        self.stdout.write(f'   /admin/quizzes/quiz/{quiz.id}/change/')
        self.stdout.write(f'   (Access via: http://localhost:8000/admin/quizzes/quiz/{quiz.id}/change/)\n')
        
        self.stdout.write(self.style.SUCCESS('You can now:'))
        self.stdout.write('   1. View the quiz in admin panel')
        self.stdout.write('   2. Share the public URL with users')
        self.stdout.write('   3. Edit questions and add more choices')
        self.stdout.write('   4. View submissions after users complete the quiz\n')
        
        self.stdout.write(self.style.WARNING('Tip: Use this quiz as a template for creating your own quizzes!\n'))
