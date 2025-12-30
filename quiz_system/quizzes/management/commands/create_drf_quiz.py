from django.core.management.base import BaseCommand
from ...models import Quiz, Question, Choice


class Command(BaseCommand):
    help = 'Create Django REST Framework quiz for testing'

    def handle(self, *args, **kwargs):
        # Check if DRF quiz already exists
        if Quiz.objects.filter(title="Django REST Framework Quiz").exists():
            self.stdout.write(self.style.WARNING('DRF quiz already exists!'))
            return

        # Create DRF quiz
        quiz = Quiz.objects.create(
            title="Django REST Framework Quiz",
            description="Test your knowledge of Django REST Framework",
            is_active=True
        )

        # Question 1: MCQ
        q1 = Question.objects.create(
            quiz=quiz,
            question_text="What is Django REST Framework?",
            question_type="MCQ",
            order=1,
            points=1
        )
        Choice.objects.create(question=q1, choice_text="A JavaScript library", is_correct=False, order=1)
        Choice.objects.create(question=q1, choice_text="A toolkit for building Web APIs in Django", is_correct=True, order=2)
        Choice.objects.create(question=q1, choice_text="A database ORM", is_correct=False, order=3)
        Choice.objects.create(question=q1, choice_text="A frontend framework", is_correct=False, order=4)

        # Question 2: MCQ
        q2 = Question.objects.create(
            quiz=quiz,
            question_text="Which class is used to convert complex data types to native Python datatypes in DRF?",
            question_type="MCQ",
            order=2,
            points=1
        )
        Choice.objects.create(question=q2, choice_text="ModelForm", is_correct=False, order=1)
        Choice.objects.create(question=q2, choice_text="Serializer", is_correct=True, order=2)
        Choice.objects.create(question=q2, choice_text="Validator", is_correct=False, order=3)
        Choice.objects.create(question=q2, choice_text="Parser", is_correct=False, order=4)

        # Question 3: MCQ
        q3 = Question.objects.create(
            quiz=quiz,
            question_text="What does APIView provide in Django REST Framework?",
            question_type="MCQ",
            order=3,
            points=1
        )
        Choice.objects.create(question=q3, choice_text="Database migrations", is_correct=False, order=1)
        Choice.objects.create(question=q3, choice_text="Template rendering", is_correct=False, order=2)
        Choice.objects.create(question=q3, choice_text="Class-based views for handling API requests", is_correct=True, order=3)
        Choice.objects.create(question=q3, choice_text="User authentication only", is_correct=False, order=4)

        # Question 4: True/False
        q4 = Question.objects.create(
            quiz=quiz,
            question_text="DRF's ModelSerializer automatically generates fields based on the model.",
            question_type="TRUE_FALSE",
            order=4,
            points=1
        )
        Choice.objects.create(question=q4, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q4, choice_text="False", is_correct=False, order=2)

        # Question 5: MCQ
        q5 = Question.objects.create(
            quiz=quiz,
            question_text="Which HTTP method is typically used to update an existing resource?",
            question_type="MCQ",
            order=5,
            points=1
        )
        Choice.objects.create(question=q5, choice_text="GET", is_correct=False, order=1)
        Choice.objects.create(question=q5, choice_text="POST", is_correct=False, order=2)
        Choice.objects.create(question=q5, choice_text="PUT", is_correct=True, order=3)
        Choice.objects.create(question=q5, choice_text="DELETE", is_correct=False, order=4)

        # Question 6: MCQ
        q6 = Question.objects.create(
            quiz=quiz,
            question_text="What is the purpose of ViewSet in DRF?",
            question_type="MCQ",
            order=6,
            points=1
        )
        Choice.objects.create(question=q6, choice_text="To define URL patterns", is_correct=False, order=1)
        Choice.objects.create(question=q6, choice_text="To combine logic for multiple related views into a single class", is_correct=True, order=2)
        Choice.objects.create(question=q6, choice_text="To validate user input", is_correct=False, order=3)
        Choice.objects.create(question=q6, choice_text="To render HTML templates", is_correct=False, order=4)

        # Question 7: MCQ
        q7 = Question.objects.create(
            quiz=quiz,
            question_text="Which authentication class is NOT built into DRF?",
            question_type="MCQ",
            order=7,
            points=1
        )
        Choice.objects.create(question=q7, choice_text="BasicAuthentication", is_correct=False, order=1)
        Choice.objects.create(question=q7, choice_text="TokenAuthentication", is_correct=False, order=2)
        Choice.objects.create(question=q7, choice_text="SessionAuthentication", is_correct=False, order=3)
        Choice.objects.create(question=q7, choice_text="OAuth2Authentication", is_correct=True, order=4)

        # Question 8: True/False
        q8 = Question.objects.create(
            quiz=quiz,
            question_text="DRF routers automatically generate URL patterns for ViewSets.",
            question_type="TRUE_FALSE",
            order=8,
            points=1
        )
        Choice.objects.create(question=q8, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q8, choice_text="False", is_correct=False, order=2)

        # Question 9: MCQ
        q9 = Question.objects.create(
            quiz=quiz,
            question_text="What does the @action decorator do in a ViewSet?",
            question_type="MCQ",
            order=9,
            points=1
        )
        Choice.objects.create(question=q9, choice_text="Adds middleware to the view", is_correct=False, order=1)
        Choice.objects.create(question=q9, choice_text="Creates custom routes for extra actions", is_correct=True, order=2)
        Choice.objects.create(question=q9, choice_text="Validates serializer data", is_correct=False, order=3)
        Choice.objects.create(question=q9, choice_text="Handles pagination", is_correct=False, order=4)

        # Question 10: MCQ
        q10 = Question.objects.create(
            quiz=quiz,
            question_text="Which status code indicates a successful POST request that created a resource?",
            question_type="MCQ",
            order=10,
            points=1
        )
        Choice.objects.create(question=q10, choice_text="200 OK", is_correct=False, order=1)
        Choice.objects.create(question=q10, choice_text="201 Created", is_correct=True, order=2)
        Choice.objects.create(question=q10, choice_text="204 No Content", is_correct=False, order=3)
        Choice.objects.create(question=q10, choice_text="202 Accepted", is_correct=False, order=4)

        # Question 11: Text
        q11 = Question.objects.create(
            quiz=quiz,
            question_text="What is the default permission class in DRF that allows unrestricted access?",
            question_type="TEXT",
            order=11,
            points=2
        )
        Choice.objects.create(question=q11, choice_text="AllowAny", is_correct=True, order=1)

        # Question 12: MCQ
        q12 = Question.objects.create(
            quiz=quiz,
            question_text="Which method in a Serializer is used to create a new instance?",
            question_type="MCQ",
            order=12,
            points=1
        )
        Choice.objects.create(question=q12, choice_text="save()", is_correct=False, order=1)
        Choice.objects.create(question=q12, choice_text="create()", is_correct=True, order=2)
        Choice.objects.create(question=q12, choice_text="validate()", is_correct=False, order=3)
        Choice.objects.create(question=q12, choice_text="to_representation()", is_correct=False, order=4)

        # Question 13: True/False
        q13 = Question.objects.create(
            quiz=quiz,
            question_text="GenericAPIView combines APIView with mixins for common operations.",
            question_type="TRUE_FALSE",
            order=13,
            points=1
        )
        Choice.objects.create(question=q13, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q13, choice_text="False", is_correct=False, order=2)

        # Question 14: MCQ
        q14 = Question.objects.create(
            quiz=quiz,
            question_text="What is throttling in DRF?",
            question_type="MCQ",
            order=14,
            points=1
        )
        Choice.objects.create(question=q14, choice_text="Speeding up API responses", is_correct=False, order=1)
        Choice.objects.create(question=q14, choice_text="Rate limiting API requests", is_correct=True, order=2)
        Choice.objects.create(question=q14, choice_text="Compressing response data", is_correct=False, order=3)
        Choice.objects.create(question=q14, choice_text="Caching API responses", is_correct=False, order=4)

        # Question 15: MCQ
        q15 = Question.objects.create(
            quiz=quiz,
            question_text="Which mixin provides the 'list' action in DRF?",
            question_type="MCQ",
            order=15,
            points=1
        )
        Choice.objects.create(question=q15, choice_text="CreateModelMixin", is_correct=False, order=1)
        Choice.objects.create(question=q15, choice_text="RetrieveModelMixin", is_correct=False, order=2)
        Choice.objects.create(question=q15, choice_text="ListModelMixin", is_correct=True, order=3)
        Choice.objects.create(question=q15, choice_text="UpdateModelMixin", is_correct=False, order=4)

        self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.title}'))
        self.stdout.write(self.style.SUCCESS(f'Total questions: {quiz.question_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total points: {quiz.total_points}'))
        self.stdout.write(self.style.SUCCESS(f'Quiz ID: {quiz.id}'))
        self.stdout.write(self.style.SUCCESS(f'URL: /quiz/{quiz.id}/'))

