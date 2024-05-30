from django.http import HttpResponse
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView   
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import (
    GetQuestionListView, CreateQuestionView, CreateUserView, GetQuestionView, 
    SubmitAnswerView, CreateTestCaseView, UpdateQuestionView, DeleteQuestionView,
    GetTestCaseView, DeleteTestCaseView, ValidateTestCasesView, GetUserQuestionInfoView,
    getQuestionAnswerView
)
urlpatterns = [
    path('health/', lambda request: HttpResponse('OK'), name='health'),
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Docs
    path('docs/', SpectacularAPIView.as_view(), name='docs'),
    path('docs/ui/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),
    # Question
    path('get/question/', GetQuestionView.as_view(), name='get_question'),
    path('get/questions/', GetQuestionListView.as_view(), name='get_questions'),
    path('get/questions/<int:week>', GetQuestionListView.as_view(), name='get_questions'),
    path('create/question/', CreateQuestionView.as_view(), name='create_question'),
    path('update/question/', UpdateQuestionView.as_view(), name='update_question'),
    path('delete/question/', DeleteQuestionView.as_view(), name='delete_question'),
    path('submit/answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('validate/testcases/', ValidateTestCasesView.as_view(), name='validate_testcases'),
    path('get/question/answer/', getQuestionAnswerView.as_view(), name='get_question_answer'),
    # TestCase
    path('create/testcase/', CreateTestCaseView.as_view(), name='create_testcase'),
    path('get/testcases/', GetTestCaseView.as_view(), name='get_testcases'),
    path('delete/testcase/', DeleteTestCaseView.as_view(), name='delete_testcase'),
    # User
    path('create/user/', CreateUserView.as_view(), name='create_user'),
    path('get/userlist/', GetUserQuestionInfoView.as_view(), name='get_userlist'),
]
