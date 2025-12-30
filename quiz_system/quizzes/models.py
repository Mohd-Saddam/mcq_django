import uuid
from django.db import models
from django.core.validators import MinValueValidator


class Quiz(models.Model):
    """Quiz model - represents a quiz with title and description"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Only active quizzes can be taken")
    published_at = models.DateTimeField(null=True, blank=True,
                                        help_text="When the quiz URL was published (URL expires after 24 hours)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())

    @property
    def is_url_expired(self):
        """Check if the quiz URL has expired (24 hours from published_at)"""
        if not self.published_at or not self.is_active:
            return True
        from django.utils import timezone
        from datetime import timedelta
        expiry_time = self.published_at + timedelta(hours=24)
        return timezone.now() > expiry_time

    def regenerate_url(self):
        """Regenerate the URL by updating published_at to now"""
        from django.utils import timezone
        self.published_at = timezone.now()
        self.is_active = True
        self.save()


class Question(models.Model):
    """Question model - represents a question in a quiz"""

    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice (Single Answer)'),
        ('TRUE_FALSE', 'True/False'),
        ('TEXT', 'Short Text Answer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0, help_text="Display order of question")
    points = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['quiz', 'order', 'created_at']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        # More concise display for dropdown selection
        question_preview = self.question_text[:80]
        if len(self.question_text) > 80:
            question_preview += "..."
        return f"[{self.get_question_type_display()}] {question_preview}"


class Choice(models.Model):
    """Choice model - represents an answer choice for MCQ and True/False questions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question', 'order', 'created_at']

    def __str__(self):
        correct = "[correct]" if self.is_correct else ""
        return f"{correct} {self.choice_text[:50]}"


class Submission(models.Model):
    """Submission model - represents a quiz attempt/submission"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    name = models.CharField(max_length=200, help_text="Submitter's name")
    email = models.EmailField(help_text="Submitter's email")
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.quiz.title} - Score: {self.score}/{self.max_score}"

    @property
    def percentage(self):
        if self.max_score == 0:
            return 0
        return round((self.score / self.max_score) * 100, 2)


class Answer(models.Model):
    """Answer model - represents a user's answer to a question"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True, help_text="For text-based questions")
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ['submission', 'question']

    def __str__(self):
        return f"Answer to: {self.question.question_text[:30]}"

