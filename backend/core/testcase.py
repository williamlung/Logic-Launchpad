import traceback

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question, TestCase
from .serializers import MessageSerializer


class TestCaseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    input = serializers.FileField(allow_empty_file=True)
    output = serializers.FileField(allow_empty_file=True)
    hidden = serializers.BooleanField(default=False)

class CreateTestCaseView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request={"multipart/form-data": TestCaseSerializer},
        responses=MessageSerializer,
        tags=['TestCase']
    )
    def post(self, request):
        try:
            if not TestCaseSerializer(data=request.data).is_valid():
                return Response({"status": False, "message": "Invalid data"})
            question_id = request.data.get('question_id')
            if not Question.objects.filter(id=question_id).exists():
                return Response({"status": False, "message": "Invalid question id"})
            input = request.data.get('input')
            output = request.data.get('output')
            hidden = request.data.get('hidden')
            hidden = True if hidden == 'true' else False
            question = Question.objects.get(id=question_id)
            test_case = TestCase(question=question, input=input, output=output, hidden=hidden)
            test_case.save()
            return Response({"status": True, "message": "Test case created successfully"})
        except:
            traceback.print_exc()
            return Response({"status": False, "message": "Unable to create test case, please contact admin"})