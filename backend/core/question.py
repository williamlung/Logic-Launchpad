import os
import shutil

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from .models import CustomUser, Question, QuestionQuota, TestCase, SubmitRecord
from .serializers import MessageSerializer

class QuestionSerializer(serializers.Serializer):
    title = serializers.CharField()
    id = serializers.IntegerField()
    finished = serializers.BooleanField()

class GetQuestionListView(APIView):
    @extend_schema(
        responses=QuestionSerializer(many=True),
        tags=['Question']
    )
    def get(self, request):
        all_questions = Question.objects.all()
        user = CustomUser.objects.get(username=request.user)
        return_questions = []
        for question in all_questions:
            this_q = {}
            this_q['title'] = question.title
            this_q['id'] = question.id
            this_q['finished'] = QuestionQuota.objects.get(user=user, question=question).passed
            return_questions.append(this_q)
        return Response(return_questions)

class QuestionDetailsSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    quota = serializers.IntegerField()
    start_code_template_file = serializers.FileField()

class GetQuestionView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="id", type=int, description="question id")
        ],
        responses={200:QuestionDetailsSerializer, 400:MessageSerializer},
        tags=['Question']
    )
    def get(self, request):
        question_id = request.query_params.get('id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        return Response({
            "title": question.title,
            "description": question.description,
            "quota": QuestionQuota.objects.get(user=request.user, question=question).quota,
            "start_code_template_file": question.start_code_template_file
        })

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
        for user in CustomUser.objects.all():
            question_quota = QuestionQuota(user=user, question=question)
            question_quota.save()
        return Response({"status": True, "message": "Question created successfully"})

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.FileField()

class SubmitAnswerView(APIView):
    @extend_schema(
        request={"multipart/form-data": SubmitAnswerSerializer},
        responses=MessageSerializer,
        tags=['Question']
    )
    def post(self, request):
        if not SubmitAnswerSerializer(data=request.data).is_valid():
            return Response({"status": False, "message": "Invalid data"})
        question_id = request.data.get('question_id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        submit_record = SubmitRecord.objects.create(user=request.user, answer=request.data.get('answer'))
        question = Question.objects.get(id=question_id)
        test_cases = TestCase.objects.filter(question=question)
        if len(test_cases) == 0:
            return Response({"status": True, "message": "No test cases to run"})
        answer_code = submit_record.answer
        answer_code = answer_code.read().replace(b'\r\n', b'\n').decode('utf-8')
        question_quota = QuestionQuota.objects.get(user=request.user, question=question)
        question_quota.quota -= 1
        question_quota.save()
        case_num, total_case_num = 1, len(test_cases)
        for test_case in test_cases:
            test_case_input = test_case.input
            test_case_output = test_case.output
            test_case_input = test_case_input.read().replace(b'\r\n', b'\n').decode('utf-8')
            test_case_output = test_case_output.read().replace(b'\r\n', b'\n').decode('utf-8')
            docker_answer = run_code_in_docker(answer_code, test_case_input)
            if docker_answer["status"]:
                if docker_answer["answer"] != test_case_output and not test_case.hidden:
                    return Response({"status": True, "message": f"Test case failed in {case_num}/{total_case_num}", "expected_output": test_case_output, "user_output": docker_answer["answer"]})
                elif docker_answer["answer"] != test_case_output and test_case.hidden:
                    return Response({"status": True, "message": "Test case failed in hidden case, good luck", "expected_output": "", "user_output": ""})
            else:
                return Response({"status": False, "message": f"Test case failed in {case_num}/{total_case_num}", "error": docker_answer["message"]})
            case_num += 1
        question_quota.passed = True
        question_quota.save()
        return Response({"status": True, "message": "All test cases passed"})

def run_code_in_docker(answer_code:str, test_case_input:str) -> str:
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    with open(os.path.join(temp_dir, "temp.c"), "w") as f:
        f.write(answer_code)
    with open(os.path.join(temp_dir, "temp.in"), "w") as f:
        f.write(test_case_input)
    run_command = "docker run --rm -v %cd%/temp:/temp gcc:latest /bin/sh -c \"gcc -o /temp/temp /temp/temp.c 2> /temp/gcc_error.txt && /temp/temp < /temp/temp.in > /temp/output.txt 2> /temp/runtime_error.txt && cat /temp/output.txt\""
    output = os.popen(run_command).read()
    if os.path.exists(os.path.join(temp_dir, "gcc_error.txt")):
        with open(os.path.join(temp_dir, "gcc_error.txt"), "r") as f:
            error_msg = f.read()
        return {"status": False, "message": error_msg}
    elif os.path.exists(os.path.join(temp_dir, "runtime_error.txt")):
        with open(os.path.join(temp_dir, "runtime_error.txt"), "r") as f:
            error_msg = f.read()
        return {"status": False, "message": error_msg}
    else:
        return {"status": True, "answer": output}