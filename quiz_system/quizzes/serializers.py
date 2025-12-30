from rest_framework import serializers
from .models import Quiz, Question, Choice, Submission, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model - hides correct answer for quiz taking"""

    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'order']


class ChoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for Choice with correct answer - for results"""

    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model with choices"""
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'points', 'order', 'choices']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for Question with correct answers shown"""
    choices = ChoiceDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'points', 'order', 'choices']


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer for Quiz list view"""
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'question_count', 'created_at']


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serializer for Quiz detail view with all questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions', 'question_count', 'total_points', 'created_at']


class AnswerSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting an answer"""
    question_id = serializers.UUIDField()
    choice_id = serializers.UUIDField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        """Ensure either choice_id or text_answer is provided"""
        if not data.get('choice_id') and not data.get('text_answer'):
            raise serializers.ValidationError("Either choice_id or text_answer must be provided")
        return data


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting a complete quiz"""
    name = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)
    answers = AnswerSubmissionSerializer(many=True)


class AnswerResultSerializer(serializers.ModelSerializer):
    """Serializer for showing answer results"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    points = serializers.IntegerField(source='question.points', read_only=True)
    your_answer = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['question_text', 'question_type', 'your_answer', 'correct_answer', 'is_correct', 'points']

    def get_your_answer(self, obj):
        """Get the user's answer"""
        if obj.choice:
            return obj.choice.choice_text
        return obj.text_answer or "No answer"

    def get_correct_answer(self, obj):
        """Get the correct answer"""
        question = obj.question
        if question.question_type in ['MCQ', 'TRUE_FALSE']:
            correct_choices = question.choices.filter(is_correct=True)
            return ", ".join([c.choice_text for c in correct_choices])
        return "Text answers are checked for exact match"


class SubmissionResultSerializer(serializers.ModelSerializer):
    """Serializer for submission results"""
    answers = AnswerResultSerializer(many=True, read_only=True)
    percentage = serializers.FloatField(read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'quiz_title', 'name', 'email', 'score', 'max_score', 'percentage', 'submitted_at', 'answers']
