from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView   
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import GetQuestionListView, CreateQuestionView, CreateUserView, GetQuestionView, SubmitAnswerView, CreateTestCaseView

urlpatterns = [
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Docs
    path('docs/', SpectacularAPIView.as_view(), name='docs'),
    path('docs/ui/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),
    # Question
    path('get/question/', GetQuestionView.as_view(), name='get_question'),
    path('get/questions/', GetQuestionListView.as_view(), name='get_questions'),
    path('get/questions/<int:week>', GetQuestionListView.as_view(), name='get_questions'),
    path('create/question/', CreateQuestionView.as_view(), name='create_question'),
    path('submit/answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    # TestCase
    path('create/testcase/', CreateTestCaseView.as_view(), name='create_testcase'),
    # User
    path('create/user/', CreateUserView.as_view(), name='create_user'),
]
