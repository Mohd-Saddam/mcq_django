from django.core.management.base import BaseCommand
from ...models import Quiz, Question, Choice


class Command(BaseCommand):
    help = 'Create sample quiz data for testing'

    def handle(self, *args, **kwargs):
        # Check if sample quiz already exists
        if Quiz.objects.filter(title="Python Programming Quiz").exists():
            self.stdout.write(self.style.WARNING('Sample quiz already exists!'))
            return

        # Create a sample quiz
        quiz = Quiz.objects.create(
            title="Python Programming Quiz",
            description="Test your knowledge of Python programming basics",
            is_active=True
        )

        # Question 1: MCQ
        q1 = Question.objects.create(
            quiz=quiz,
            question_text="What is the output of: print(2 ** 3)?",
            question_type="MCQ",
            order=1,
            points=1
        )
        Choice.objects.create(question=q1, choice_text="5", is_correct=False, order=1)
        Choice.objects.create(question=q1, choice_text="6", is_correct=False, order=2)
        Choice.objects.create(question=q1, choice_text="8", is_correct=True, order=3)
        Choice.objects.create(question=q1, choice_text="9", is_correct=False, order=4)

        # Question 2: True/False
        q2 = Question.objects.create(
            quiz=quiz,
            question_text="Python is a statically typed programming language.",
            question_type="TRUE_FALSE",
            order=2,
            points=1
        )
        Choice.objects.create(question=q2, choice_text="True", is_correct=False, order=1)
        Choice.objects.create(question=q2, choice_text="False", is_correct=True, order=2)

        # Question 3: Text
        q3 = Question.objects.create(
            quiz=quiz,
            question_text="What keyword is used to define a function in Python?",
            question_type="TEXT",
            order=3,
            points=2
        )
        Choice.objects.create(question=q3, choice_text="def", is_correct=True, order=1)

        # Question 4: MCQ
        q4 = Question.objects.create(
            quiz=quiz,
            question_text="Which of the following is NOT a valid Python data type?",
            question_type="MCQ",
            order=4,
            points=1
        )
        Choice.objects.create(question=q4, choice_text="list", is_correct=False, order=1)
        Choice.objects.create(question=q4, choice_text="tuple", is_correct=False, order=2)
        Choice.objects.create(question=q4, choice_text="array", is_correct=True, order=3)
        Choice.objects.create(question=q4, choice_text="dict", is_correct=False, order=4)

        # Question 5: True/False
        q5 = Question.objects.create(
            quiz=quiz,
            question_text="Lists in Python are mutable.",
            question_type="TRUE_FALSE",
            order=5,
            points=1
        )
        Choice.objects.create(question=q5, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q5, choice_text="False", is_correct=False, order=2)

        self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.title}'))
        self.stdout.write(self.style.SUCCESS(f'Total questions: {quiz.question_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total points: {quiz.total_points}'))
        self.stdout.write(self.style.SUCCESS(f'Quiz ID: {quiz.id}'))
        self.stdout.write(self.style.SUCCESS(f'URL: /quiz/{quiz.id}/ (Access via http://localhost:8000 or http://127.0.0.1:8000)'))
