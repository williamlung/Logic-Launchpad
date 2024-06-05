import os
import shutil
import subprocess

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

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
    def get(self, request, week=settings.WEEK):
        all_questions = Question.objects.filter(week=week)
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
        if request.user.is_superuser:
            code = question.start_code_template_file
        else:
            srs = SubmitRecord.objects.filter(user=request.user, question=question)
            if srs.exists():
                code = srs.last().answer
                print(code)
            else:
                code = question.start_code_template_file
        return Response({
            "title": question.title,
            "description": question.description,
            "quota": QuestionQuota.objects.get(user=request.user, question=question).quota,
            "start_code_template_file": code
        })

class CreateQuestionSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    week = serializers.IntegerField()
    start_code_template_file = serializers.FileField()

class ResponseCreateQuestionSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    id = serializers.IntegerField()

class CreateQuestionView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request={"multipart/form-data": CreateQuestionSerializer},
        responses={"200": ResponseCreateQuestionSerializer, "400": MessageSerializer},
        tags=['Question']
    )
    def post(self, request):
        if not CreateQuestionSerializer(data=request.data).is_valid():
            return Response({"status": False, "message": "Invalid data"}, status=400)
        title = request.data.get('title')
        description = request.data.get('description')
        week = request.data.get('week')
        start_code_template_file = request.data.get('start_code_template_file')
        question = Question(title=title, description=description, week=week, start_code_template_file=start_code_template_file)
        question.save()
        for user in CustomUser.objects.all():
            question_quota = QuestionQuota(user=user, question=question)
            question_quota.save()
        return Response({"status": True, "message": "Question created successfully", "id": question.id})

class UpdateQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    start_code_template_file = serializers.FileField(allow_empty_file=True)

class UpdateQuestionView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request={"multipart/form-data": UpdateQuestionSerializer},
        responses=MessageSerializer,
        tags=['Question']
    )
    def post(self, request):
        if not UpdateQuestionSerializer(data=request.data).is_valid():
            return Response({"status": False, "message": "Invalid data"})
        question_id = request.data.get('id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        question.title = request.data.get('title')
        question.description = request.data.get('description')
        question.start_code_template_file = request.data.get('start_code_template_file')
        question.save()
        return Response({"status": True, "message": "Question updated successfully"})

class DeleteQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class DeleteQuestionView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request=DeleteQuestionSerializer,
        responses=MessageSerializer,
        tags=['Question']
    )
    def post(self, request):
        if not DeleteQuestionSerializer(data=request.data).is_valid():
            return Response({"status": False, "message": "Invalid data"})
        question_id = request.data.get('id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        question.delete()
        return Response({"status": True, "message": "Question deleted successfully"})

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.FileField(allow_empty_file=True)

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
        question = Question.objects.get(id=question_id)
        submit_record = SubmitRecord.objects.create(user=request.user, answer=request.data.get('answer'), question=question)
        test_cases = TestCase.objects.filter(question=question)
        answer_code = submit_record.answer
        answer_code = answer_code.read().replace(b'\r\n', b'\n').decode('utf-8')
        question_quota = QuestionQuota.objects.get(user=request.user, question=question)
        if question_quota.quota == 0:
            return Response({"status": False, "message": "You have no quota left for this question"})
        question_quota.quota -= 1
        question_quota.save()
        case_num, total_case_num = 1, len(test_cases)
        # do the non-hidden test cases first
        test_cases = test_cases.order_by('hidden')
        for test_case in test_cases:
            test_case_input = test_case.input
            test_case_output = test_case.output
            test_case_input_text = test_case_input.read().replace(b'\r\n', b'\n').decode('utf-8')
            test_case_output_text = test_case_output.read().replace(b'\r\n', b'\n').decode('utf-8')
            test_case_input.close()
            test_case_output.close()
            docker_answer = run_code_in_docker(answer_code, test_case_input_text)
            if docker_answer["status"]:
                if docker_answer["answer"] != test_case_output_text and not test_case.hidden:
                    return Response({"status": False, "message": f"Test case failed in {case_num}/{total_case_num}\nInput:\n{test_case_input_text}\nExpected output:\n{test_case_output_text}\nYour output:\n{docker_answer['answer']}"})
                elif docker_answer["answer"] != test_case_output_text and test_case.hidden:
                    return Response({"status": False, "message": f"Test case failed in hidden case{case_num}/{total_case_num}, good luck"})
            else:
                return Response({"status": False, "message": f"Test case failed in {case_num}/{total_case_num},\n Error: {docker_answer['message']}"})
            case_num += 1
        question_quota.passed = True
        question_quota.save()
        return Response({"status": True, "message": "All test cases passed"})

class ValidateTestCasesSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    code = serializers.FileField(allow_empty_file=True)

class ValidateTestCasesView(APIView):
    permission_classes = [IsAdminUser]
    @extend_schema(
        request=ValidateTestCasesSerializer,
        responses=MessageSerializer,
        tags=['Question']
    )
    def post(self, request):
        this_serializer = ValidateTestCasesSerializer(data=request.data)
        if not this_serializer.is_valid():
            return Response({"status": False, "message": "Invalid data: "+str(this_serializer.errors)})
        question_id = request.data.get('question_id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        test_cases = TestCase.objects.filter(question=question)
        answer_code = request.data.get('code')
        answer_code = answer_code.read().replace(b'\r\n', b'\n').decode('utf-8')
        case_num, total_case_num = 1, len(test_cases)
        for test_case in test_cases:
            test_case_input = test_case.input
            test_case_output = test_case.output
            test_case_input_text = test_case_input.read().replace(b'\r\n', b'\n').decode('utf-8')
            test_case_output_text = test_case_output.read().replace(b'\r\n', b'\n').decode('utf-8')
            test_case_input.close()
            test_case_output.close()
            docker_answer = run_code_in_docker(answer_code, test_case_input_text)
            if docker_answer["status"]:
                if docker_answer["answer"] != test_case_output_text:
                    return Response({"status": False, "message": f"Test case failed in {case_num}/{total_case_num}\nInput:\n{test_case_input_text}\nExpected output:\n{test_case_output_text}\nYour output:{docker_answer['answer']}"})
            else:
                return Response({"status": False, "message": f"Test case failed in {case_num}/{total_case_num},\n Error: {docker_answer['message']}"})
            case_num += 1
        return Response({"status": True, "message": "All test cases passed"})


class ModelAnswerSerializer(serializers.Serializer):
    answer = serializers.FileField()

class getQuestionAnswerView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name="question_id", type=int, description="question id")
        ],
        responses={200:ModelAnswerSerializer, 400:MessageSerializer},
        tags=['Question']
    )
    def get(self, request):
        question_id = request.query_params.get('question_id')
        if not Question.objects.filter(id=question_id).exists():
            return Response({"status": False, "message": "Invalid question id"})
        question = Question.objects.get(id=question_id)
        sr = SubmitRecord.objects.filter(user=request.user, question=question)
        if len(sr) == 0:
            return Response({"status": False, "message": "No answer found"})
        answer_code = sr.last().answer
        answer_code = answer_code.read().replace(b'\r\n', b'\n').decode('utf-8')
        return Response({
            "answer": answer_code
        })


def run_code_in_docker(answer_code:str, test_case_input:str) -> str:
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    with open(os.path.join(temp_dir, "temp.c"), "w", encoding="big5") as f:
        f.write(answer_code)
    with open(os.path.join(temp_dir, "temp.in"), "w", encoding="big5") as f:
        f.write(test_case_input)
    run_command = "docker run --rm -v \"%cd%\"/temp:/temp gcc:latest /bin/sh -c \"gcc -finput-charset=utf-8 -o /temp/temp /temp/temp.c 2> /temp/gcc_error.txt && /temp/temp < /temp/temp.in > /temp/output.txt 2> /temp/runtime_error.txt && cat /temp/output.txt\""
    output = ""
    command_output = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = command_output.communicate()
    output = output.decode("big5")
    if error:
        return {"status": False, "message": error}
    if os.path.exists(os.path.join(temp_dir, "gcc_error.txt")):
        with open(os.path.join(temp_dir, "gcc_error.txt"), "r", encoding="big5") as f:
            error_msg = f.read()
        if len(error_msg) != 0:
            return {"status": False, "message": error_msg}
    if os.path.exists(os.path.join(temp_dir, "runtime_error.txt")):
        with open(os.path.join(temp_dir, "runtime_error.txt"), "r", encoding="big5") as f:
            error_msg = f.read()
        if len(error_msg) != 0:
            return {"status": False, "message": error_msg}
        
    return {"status": True, "answer": output}
