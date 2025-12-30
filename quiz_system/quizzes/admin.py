from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Quiz, Question, Choice, Submission, Answer


def get_base_url(request):
    """Get dynamic base URL from request"""
    scheme = request.scheme  # 'http' or 'https'
    host = request.get_host()  # 'localhost:8000' or '127.0.0.1:8000' or domain
    return f"{scheme}://{host}"


class AdminRequestMiddleware:
    """Middleware to attach request to admin site for dynamic URL generation"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            admin.site._request = request
        response = self.get_response(request)
        return response


class ChoiceInline(admin.TabularInline):
    """Inline admin for managing choices within a question"""
    model = Choice
    extra = 1
    fields = ['choice_text', 'is_correct', 'order']


class QuestionInline(admin.StackedInline):
    """Inline admin for managing questions within a quiz"""
    model = Question
    extra = 1
    show_change_link = True
    fields = ['question_text', 'question_type', 'points', 'order']
    readonly_fields = ['usage_hint']

    def usage_hint(self, obj):
        """Display helpful instructions for adding choices"""
        if obj and obj.pk:
            return format_html(
                '<div style="background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; border-radius: 4px; margin: 10px 0;">'
                '<strong>To Add/Edit Answer Choices:</strong><br>'
                'Click the "Change" link above to edit this question and add answer choices.'
                '</div>'
            )
        return format_html(
            '<div style="background: #d1ecf1; padding: 12px; border-left: 4px solid #17a2b8; border-radius: 4px; margin: 10px 0;">'
            '<strong>Important:</strong><br>'
            '1. Enter <strong>only the question text</strong> here (without choices)<br>'
            '2. After saving the quiz, click "Change" next to each question<br>'
            '3. Then you can add answer choices for MCQ/True-False questions'
            '</div>'
        )

    usage_hint.short_description = ""

    class Media:
        css = {
            'all': ('admin/css/custom_question_inline.css',)
        }
        js = ('admin/js/question_inline.js',)

    def save_formset(self, request, form, formset, change):
        """Override to handle copying of existing questions with their choices"""
        instances = formset.save(commit=False)

        for form_instance in formset.forms:
            if hasattr(form_instance, 'cleaned_data'):
                existing_question = form_instance.cleaned_data.get('existing_question')

                if existing_question and form_instance.instance.pk is None:
                    # This is a new question being created from an existing one
                    new_question = form_instance.instance
                    new_question.save()  # Save the question first

                    # Copy all choices from the existing question
                    for existing_choice in existing_question.choices.all():
                        Choice.objects.create(
                            question=new_question,
                            choice_text=existing_choice.choice_text,
                            is_correct=existing_choice.is_correct,
                            order=existing_choice.order
                        )

        # Call parent save to handle normal saves
        super().save_formset(request, form, formset, change)

        # Delete objects marked for deletion
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin interface for Quiz model"""
    list_display = ['title', 'is_active', 'url_status', 'public_url_display', 'question_count', 'total_points',
                    'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'public_url_field', 'add_existing_questions_link']
    inlines = [QuestionInline]
    actions = ['regenerate_url_action']

    def regenerate_url_action(self, request, queryset):
        """Admin action to regenerate URLs for selected quizzes"""
        count = 0
        for quiz in queryset:
            quiz.regenerate_url()
            count += 1
        self.message_user(request,
                          f'Successfully regenerated URLs for {count} quiz(zes). URLs are now valid for 24 hours.')

    regenerate_url_action.short_description = "Regenerate URL (reset 24-hour timer)"

    def add_existing_questions_link(self, obj):
        """Display a link to add existing questions"""
        if obj.pk:
            from django.urls import reverse
            url = reverse('admin:add_existing_questions', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background: #417690; color: white; padding: 10px 20px; '
                'border-radius: 4px; text-decoration: none; display: inline-block;">'
                'Add Existing Questions to This Quiz</a>',
                url
            )
        return "Save the quiz first to add existing questions"

    add_existing_questions_link.short_description = "Reuse Questions"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:quiz_id>/add-existing-questions/',
                 self.admin_site.admin_view(self.add_existing_questions_view),
                 name='add_existing_questions'),
        ]
        return custom_urls + urls

    def add_existing_questions_view(self, request, quiz_id):
        """Custom view to add existing questions to a quiz"""
        from django.shortcuts import render, redirect, get_object_or_404
        from django.contrib import messages

        quiz = get_object_or_404(Quiz, pk=quiz_id)

        if request.method == 'POST':
            selected_questions = request.POST.getlist('questions')
            added_count = 0

            for question_id in selected_questions:
                try:
                    original_question = Question.objects.get(pk=question_id)

                    # Create a copy of the question for this quiz
                    new_question = Question.objects.create(
                        quiz=quiz,
                        question_text=original_question.question_text,
                        question_type=original_question.question_type,
                        points=original_question.points,
                        order=quiz.questions.count()
                    )

                    # Copy all choices
                    for choice in original_question.choices.all():
                        Choice.objects.create(
                            question=new_question,
                            choice_text=choice.choice_text,
                            is_correct=choice.is_correct,
                            order=choice.order
                        )
                    added_count += 1
                except Exception as e:
                    messages.error(request, f"Error adding question: {e}")

            if added_count > 0:
                messages.success(request, f"Successfully added {added_count} question(s) to '{quiz.title}'")

            return redirect('admin:quizzes_quiz_change', quiz_id)

        # Get all questions not already in this quiz (by question_text)
        existing_texts = quiz.questions.values_list('question_text', flat=True)
        available_questions = Question.objects.exclude(
            question_text__in=existing_texts
        ).select_related('quiz').order_by('-created_at')

        context = {
            'title': f'Add Existing Questions to: {quiz.title}',
            'quiz': quiz,
            'available_questions': available_questions,
            'opts': self.model._meta,
            'has_change_permission': True,
        }

        return render(request, 'admin/quizzes/add_existing_questions.html', context)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Public Access', {
            'fields': ('public_url_field',),
            'description': 'Share this URL with users to take the quiz'
        }),
        ('Reuse Questions', {
            'fields': ('add_existing_questions_link',),
            'description': 'Add questions from other quizzes',
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def public_url_field(self, obj):
        """Display the public quiz URL in the admin form with live countdown timer"""
        if obj.pk:
            from django.utils.html import format_html
            from django.utils import timezone
            from datetime import timedelta
            from django.contrib.admin import site

            # Get current request to build dynamic URL
            request = getattr(site, '_request', None)
            if request:
                base_url = get_base_url(request)
                url = f"{base_url}/quiz/{obj.id}/"
            else:
                # Fallback if request not available
                url = f"/quiz/{obj.id}/"

            # Check if URL is active and has expiry
            timer_html = ''
            if obj.is_active and obj.published_at:
                expiry_time = obj.published_at + timedelta(hours=24)
                if timezone.now() < expiry_time:
                    expiry_iso = expiry_time.isoformat()
                    timer_html = format_html(
                        '<div id="url-timer" style="margin-top: 15px; padding: 12px; background: #e8f5e9; border-radius: 4px; border-left: 3px solid #4caf50;">'
                        '<strong style="color: #2e7d32;">URL Expires In:</strong><br>'
                        '<span id="countdown-timer" data-expiry="{}" style="font-size: 18px; font-weight: bold; color: #1b5e20; font-family: monospace;">'
                        'Loading...'
                        '</span>'
                        '</div>'
                        '<script>'
                        '(function() {{'
                        '    const expiryDate = new Date("{}");'
                        '    '
                        '    function updateTimer() {{'
                        '        const now = new Date();'
                        '        const timeLeft = expiryDate - now;'
                        '        '
                        '        if (timeLeft <= 0) {{'
                        '            document.getElementById("countdown-timer").innerHTML = '
                        '                "<span style=\\"color: #d32f2f;\\">Expired - Please regenerate URL</span>";'
                        '            return;'
                        '        }}'
                        '        '
                        '        const hours = Math.floor(timeLeft / (1000 * 60 * 60));'
                        '        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));'
                        '        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);'
                        '        '
                        '        document.getElementById("countdown-timer").innerHTML = '
                        '            hours + "h " + '
                        '            String(minutes).padStart(2, "0") + "m " + '
                        '            String(seconds).padStart(2, "0") + "s";'
                        '        '
                        '        setTimeout(updateTimer, 1000);'
                        '    }}'
                        '    '
                        '    updateTimer();'
                        '}})()'
                        '</script>',
                        expiry_iso,
                        expiry_iso
                    )
                else:
                    timer_html = format_html(
                        '<div style="margin-top: 15px; padding: 12px; background: #ffebee; border-radius: 4px; border-left: 3px solid #f44336;">'
                        '<strong style="color: #c62828;">URL Expired</strong><br>'
                        '<span style="font-size: 13px; color: #666;">Use "Regenerate URL" action to create a new valid URL</span>'
                        '</div>'
                    )

            return format_html(
                '<div style="background: #f0f0f0; padding: 15px; border-radius: 5px; border-left: 4px solid #417690;">'
                '<p style="margin: 0 0 10px 0; font-weight: bold; color: #333;">Public Quiz URL:</p>'
                '<input type="text" value="{}" readonly '
                'style="width: 100%; padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 3px; font-family: monospace;" '
                'onclick="this.select(); document.execCommand(\'copy\'); '
                'alert(\'URL copied to clipboard!\');" />'
                '<p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">Click the URL to copy it to clipboard</p>'
                '{}'
                '</div>',
                url,
                timer_html
            )
        return "Save the quiz first to generate a public URL"

    public_url_field.short_description = "Public Quiz URL"

    def public_url_display(self, obj):
        """Display a short URL indicator in the list view"""
        if obj.pk:
            from django.utils.html import format_html
            url = f"/quiz/{obj.id}/"
            return format_html(
                '<a href="{}" target="_blank" style="color: #417690; text-decoration: none;" '
                'title="Click to open quiz">View</a>',
                url
            )
        return "-"

    public_url_display.short_description = "Public URL"

    def url_status(self, obj):
        """Display URL status (Active/Expired) in list view with live countdown timer"""
        if not obj.is_active:
            return format_html('<span style="color: #999;">Inactive</span>')
        if not obj.published_at:
            return format_html('<span style="color: #ff9800;">Not Published</span>')
        if obj.is_url_expired:
            return format_html('<span style="color: #f44336;">Expired</span>')

        from django.utils import timezone
        from datetime import timedelta
        import json

        # Calculate expiry time
        expiry_time = obj.published_at + timedelta(hours=24)
        time_left = expiry_time - timezone.now()

        # Get total seconds left
        total_seconds = int(time_left.total_seconds())

        # Create unique ID for this timer
        timer_id = f"timer-{obj.id}"

        # Convert to ISO format for JavaScript
        expiry_iso = expiry_time.isoformat()

        return format_html(
            '<div style="display: inline-block;">'
            '<span style="color: #4caf50; font-weight: bold;">Active</span><br>'
            '<span id="{}" data-expiry="{}" style="font-size: 11px; color: #666; font-family: monospace;">'
            'Loading timer...'
            '</span>'
            '</div>'
            '<script>'
            '(function() {{'
            '    const timerId = "{}";'
            '    const expiryDate = new Date("{}");'
            '    '
            '    function updateTimer() {{'
            '        const now = new Date();'
            '        const timeLeft = expiryDate - now;'
            '        '
            '        if (timeLeft <= 0) {{'
            '            document.getElementById(timerId).innerHTML = "<span style=\\"color: #f44336;\\">Expired</span>";'
            '            return;'
            '        }}'
            '        '
            '        const hours = Math.floor(timeLeft / (1000 * 60 * 60));'
            '        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));'
            '        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);'
            '        '
            '        document.getElementById(timerId).innerHTML = '
            '            hours + "h " + '
            '            String(minutes).padStart(2, "0") + "m " + '
            '            String(seconds).padStart(2, "0") + "s";'
            '        '
            '        setTimeout(updateTimer, 1000);'
            '    }}'
            '    '
            '    updateTimer();'
            '}})()'
            '</script>',
            timer_id,
            expiry_iso,
            timer_id,
            expiry_iso
        )

    url_status.short_description = "URL Status"

    def save_model(self, request, obj, form, change):
        """Override save to set published_at and show success message with public URL"""
        # Set published_at when quiz is being activated
        if obj.is_active and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)
        from django.contrib import messages
        from django.utils.html import format_html

        if obj.is_active and obj.published_at:
            base_url = get_base_url(request)
            url = f"{base_url}/quiz/{obj.id}/"
            from datetime import timedelta
            expiry_time = obj.published_at + timedelta(hours=24)
            messages.success(
                request,
                format_html(
                    'Quiz "{}" is now published!<br>'
                    '<strong>Public URL:</strong> <a href="{}" target="_blank" style="color: #fff; text-decoration: underline;">{}</a><br>'
                    '<strong>URL expires:</strong> {} (24 hours from now)<br>'
                    'Share this URL with users to take the quiz.',
                    obj.title,
                    url,
                    url,
                    expiry_time.strftime('%B %d, %Y at %I:%M %p')
                )
            )
        else:
            messages.info(request, f'Quiz "{obj.title}" saved as draft (not published).')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model"""
    list_display = ['question_preview', 'quiz', 'question_type', 'choice_count', 'points', 'order', 'created_at']
    list_filter = ['question_type', 'quiz', 'created_at']
    search_fields = ['question_text', 'quiz__title']
    readonly_fields = ['created_at', 'choice_info']
    inlines = [ChoiceInline]
    date_hierarchy = 'created_at'

    def question_preview(self, obj):
        """Show a preview of the question text"""
        preview = obj.question_text[:100]
        if len(obj.question_text) > 100:
            preview += "..."
        return preview

    question_preview.short_description = "Question Text"

    def choice_count(self, obj):
        """Display the number of choices for this question"""
        count = obj.choices.count()
        if obj.question_type in ['MCQ', 'TRUE_FALSE'] and count == 0:
            return format_html('<span style="color: red; font-weight: bold;">0 choices</span>')
        elif count > 0:
            correct = obj.choices.filter(is_correct=True).count()
            return format_html('<span style="color: green;">{} ({} correct)</span>', count, correct)
        return '-'

    choice_count.short_description = "Choices"

    def choice_info(self, obj):
        """Display information about adding choices"""
        if obj and obj.pk:
            count = obj.choices.count()
            if obj.question_type in ['MCQ', 'TRUE_FALSE']:
                if count == 0:
                    return format_html(
                        '<div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 4px;">'
                        '<strong>No Choices Added Yet!</strong><br><br>'
                        'Use the "Choices" section below to add answer options for this MCQ question.<br>'
                        'Click "Add another Choice" to create each answer option.'
                        '</div>'
                    )
                else:
                    correct = obj.choices.filter(is_correct=True).count()
                    return format_html(
                        '<div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; border-radius: 4px;">'
                        '<strong>{} Choice(s) Added</strong> ({} marked as correct)<br>'
                        'You can add more or edit existing choices below.'
                        '</div>',
                        count, correct
                    )
        return ""

    choice_info.short_description = ""

    fieldsets = (
        ('Question Details', {
            'fields': ('quiz', 'question_text', 'question_type', 'points', 'order')
        }),
        ('Answer Choices', {
            'fields': ('choice_info',),
            'description': 'Add answer choices below using the Choices section'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """Admin interface for Choice model"""
    list_display = ['__str__', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['choice_text', 'question__question_text']
    readonly_fields = ['created_at']


class AnswerInline(admin.TabularInline):
    """Inline admin for viewing answers within a submission"""
    model = Answer
    extra = 0
    readonly_fields = ['question', 'choice', 'text_answer', 'is_correct']
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model"""
    list_display = ['quiz', 'name', 'email', 'score', 'max_score', 'percentage', 'submitted_at']
    list_filter = ['quiz', 'submitted_at']
    search_fields = ['quiz__title', 'name', 'email']
    readonly_fields = ['quiz', 'name', 'email', 'score', 'max_score', 'submitted_at']
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        # Submissions should only be created through the API
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin interface for Answer model"""
    list_display = ['__str__', 'submission', 'question', 'is_correct']
    list_filter = ['is_correct', 'submission__quiz']
    search_fields = ['question__question_text', 'text_answer']
    readonly_fields = ['submission', 'question', 'choice', 'text_answer', 'is_correct']

    def has_add_permission(self, request):
        # Answers should only be created through the API
        return False
