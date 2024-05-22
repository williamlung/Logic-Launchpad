from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from .models import CustomUser, Question, QuestionQuota
from .serializers import MessageSerializer

class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class CreateUserView(APIView):
    @extend_schema(
        request=CreateUserSerializer,
        responses=MessageSerializer,
        tags=['User']
    )
    def post(self, request):
        try:
            if not CreateUserSerializer(data=request.data).is_valid():
                return Response({"status": False, "message": "Invalid data"})
            username = request.data.get('username')
            if CustomUser.objects.filter(username=username).exists():
                return Response({"status": False, "message": "User already exists"})
            password = request.data.get('password')
            user = CustomUser(username=username)
            user.set_password(password)
            user.save()
            all_questions = Question.objects.all()
            for question in all_questions:
                question_quota = QuestionQuota(user=user, question=question)
                question_quota.save()
            return Response({"status": True, "message": "User created successfully"})
        except:
            return Response({"status": False, "message": "Unable to create user, please contact admin"})