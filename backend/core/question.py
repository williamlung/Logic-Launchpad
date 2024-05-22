from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from .models import CustomUser, Question, QuestionQuota
from .serializers import MessageSerializer

class QuestionSerializer(serializers.Serializer):
    title = serializers.CharField()
    id = serializers.IntegerField()
    finished = serializers.BooleanField()

class GetQuestionListView(APIView):
    @extend_schema(
        request=None,
        responses=QuestionSerializer(many=True),
        tags=['Question']
    )
    def get(self, request):
        all_questions = Question.objects.all()
        user = CustomUser.objects.get(username=request.user)
        return_questions = []
        qid = 1
        for question in all_questions:
            this_q = {}
            this_q['title'] = question.title
            this_q['id'] = qid
            this_q['finished'] = QuestionQuota.objects.get(user=user, question=question).passed
            return_questions.append(question)
            qid += 1
        return Response(return_questions)

class CreateQuestionSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    week = serializers.IntegerField()
    start_code_template_file = serializers.FileField()

class CreateQuestionView(APIView):
    @extend_schema(
        request={"multipart/form-data": CreateQuestionSerializer},
        responses=MessageSerializer,
        tags=['Question']
    )
    def post(self, request):
        if not CreateQuestionSerializer(data=request.data).is_valid():
            return Response({"status": False, "message": "Invalid data"})
        title = request.data.get('title')
        description = request.data.get('description')
        week = request.data.get('week')
        start_code_template_file = request.data.get('start_code_template_file')
        question = Question(title=title, description=description, week=week, start_code_template_file=start_code_template_file)
        question.save()
        # need to create question quota for all users
        for user in CustomUser.objects.all():
            question_quota = QuestionQuota(user=user, question=question)
            question_quota.save()
        return Response({"status": True, "message": "Question created successfully"})
