import traceback

from drf_spectacular.utils import extend_schema, OpenApiParameter
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
            question = Question.objects.get(id=question_id)
            test_case = TestCase(question=question, input=input, output=output, hidden=hidden)
            test_case.save()
            return Response({"status": True, "message": "Test case created successfully"})
        except:
            traceback.print_exc()
            return Response({"status": False, "message": "Unable to create test case, please contact admin"})

class ResponseTestCaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    input = serializers.CharField()
    output = serializers.CharField()
    hidden = serializers.BooleanField()

class GetTestCaseView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        parameters=[OpenApiParameter(name='question_id', type=int)],
        responses=ResponseTestCaseSerializer(many=True),
        tags=['TestCase']
    )
    def get(self, request):
        try:
            question_id = request.query_params.get('question_id')
            if not Question.objects.filter(id=question_id).exists():
                return Response({"status": False, "message": "Invalid question id"})
            test_cases = TestCase.objects.filter(question_id=question_id)
            test_cases = test_cases.order_by('hidden')
            return_data = []
            for test_case in test_cases:
                return_data.append({
                    "id": test_case.id,
                    "input": test_case.input,
                    "output": test_case.output,
                    "hidden": test_case.hidden
                })
            return Response(return_data)
        except:
            traceback.print_exc()
            return Response({"status": False, "message": "Unable to get test cases, please contact admin"})

class DeleteTestCaseView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        parameters=[OpenApiParameter(name='test_case_id', type=int)],
        responses=MessageSerializer,
        tags=['TestCase']
    )
    def delete(self, request):
        try:
            test_case_id = request.query_params.get('test_case_id')
            if not TestCase.objects.filter(id=test_case_id).exists():
                return Response({"status": False, "message": "Invalid test case id"})
            test_case = TestCase.objects.get(id=test_case_id)
            test_case.delete()
            return Response({"status": True, "message": "Test case deleted successfully"})
        except:
            traceback.print_exc()
            return Response({"status": False, "message": "Unable to delete test case, please contact admin"})
