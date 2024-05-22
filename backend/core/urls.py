from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView   
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import GetQuestionListView, CreateQuestionView, CreateUserView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('docs/', SpectacularAPIView.as_view(), name='docs'),
    path('docs/ui/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),
    path('get/questions/', GetQuestionListView.as_view(), name='get_questions'),
    path('create/question/', CreateQuestionView.as_view(), name='create_question'),
    path('create/user/', CreateUserView.as_view(), name='create_user'),
]
