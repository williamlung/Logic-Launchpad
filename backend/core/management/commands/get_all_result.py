from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Question, SubmitRecord, CustomUser, QuestionQuota
import os

class Command(BaseCommand):
    help = 'Export all submited results if the question is finished'
    def add_arguments(self, parser):
        parser.add_argument('output_path', type=str, help='Path to export all results')

    def handle(self, *args, **kwargs):
        # export all results to specific path from args
        if not os.path.exists(kwargs['output_path']):
            self.stdout.write('Output path does not exist')
            return
        output_path = kwargs['output_path']
        os.makedirs(output_path, exist_ok=True)
        week = settings.WEEK
        questions = Question.objects.filter(week=week)
        users = CustomUser.objects.all()
        id = 1
        for question in questions:
            self.stdout.write(f'Exporting results for question: {question.title}')
            question_folder = os.path.join(output_path, str(id)+". "+question.title)
            os.makedirs(question_folder, exist_ok=True)
            for user in users:
                if user.is_superuser:
                    continue
                qq = QuestionQuota.objects.get(user=user, question=question)
                if qq.passed:
                    submit_record = SubmitRecord.objects.filter(user=user, question=question).last()
                    sbr_file = submit_record.answer.read()
                    with open(os.path.join(question_folder, f'{user.username}.c'), 'wb') as f:
                        f.write(sbr_file)
            id += 1
                    
        self.stdout.write('Export all results complete.')