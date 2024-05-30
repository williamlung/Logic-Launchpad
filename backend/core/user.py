from django.http import JsonResponse
from django.utils.timezone import localtime
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Question, QuestionQuota
from .serializers import MessageSerializer

class ResponseUserQuestionInfoSerializer(serializers.Serializer):
    username = serializers.CharField()
    quota = serializers.IntegerField()
    finished = serializers.BooleanField()
    last_submit_time = serializers.DateTimeField()

class GetUserQuestionInfoView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        parameters=[OpenApiParameter(name='question_id', type=int)],
        responses=ResponseUserQuestionInfoSerializer(many=True),
        tags=['User']
    )
    def get(self, request):
        question_id = request.query_params.get('question_id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        all_users = CustomUser.objects.all()
        return_users = []
        for user in all_users:
            user_info = {}
            qq = QuestionQuota.objects.get(user=user, question=question)
            submit_records = user.submitrecord_set.filter(question=question)
            if submit_records.exists():
                time = submit_records.latest('created_at').created_at
                time = localtime(time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                time = "N/A"
            user_info['username'] = user.username
            user_info['quota'] = qq.quota
            user_info['finished'] = qq.passed
            user_info['last_submit_time'] = time
            return_users.append(user_info)
        return Response(return_users)

class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class CreateUserView(APIView):
    permission_classes = [IsAdminUser]
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
    
class UpdateUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UpdateUserView(APIView):
    @extend_schema(
        request=UpdateUserSerializer,
        responses=MessageSerializer,
        tags=['User']
    )
    def put(self, request):
        try:
            if not UpdateUserSerializer(data=request.data).is_valid():
                return Response({"status": False, "message": "Invalid data"})
            username = request.data.get('username')
            if not CustomUser.objects.filter(username=username).exists():
                return Response({"status": False, "message": "User does not exist"})
            if request.user.username != username and not request.user.is_superuser:
                return Response({"status": False, "message": "You can only update your own password"})
            password = request.data.get('password')
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.save()
            return Response({"status": True, "message": "User updated successfully"})
        except:
            return Response({"status": False, "message": "Unable to update user, please contact admin"})
        
class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField()

class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request=DeleteUserSerializer,
        responses=MessageSerializer,
        tags=['User']
    )
    def delete(self, request):
        try:
            if not DeleteUserSerializer(data=request.data).is_valid():
                return Response({"status": False, "message": "Invalid data"})
            username = request.data.get('username')
            if not CustomUser.objects.filter(username=username).exists():
                return Response({"status": False, "message": "User does not exist"})
            user = CustomUser.objects.get(username=username)
            user.delete()
            return Response({"status": True, "message": "User deleted successfully"})
        except:
            return Response({"status": False, "message": "Unable to delete user, please contact admin"})
        
def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if not CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'User does not exist'})
        
        user = CustomUser.objects.get(username=username)
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(password):
            return JsonResponse({'success': False, 'message': 'Invalid password'})
        
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'New passwords do not match'})
        
        user.set_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Password reset successfully'})
    
    return render(request, 'reset_password.html')