from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, SubmissionViewSet, quiz_page, index_page, quiz_urls_admin, get_question_api, get_all_questions_api

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', index_page, name='index'),
    path('api/', include(router.urls)),
    path('api/question/<uuid:question_id>/', get_question_api, name='get_question_api'),
    path('api/questions/', get_all_questions_api, name='get_all_questions_api'),
    path('quiz/<uuid:quiz_id>/', quiz_page, name='quiz_page'),
    path('admin/quiz-urls/', quiz_urls_admin, name='quiz_urls_admin'),
]
