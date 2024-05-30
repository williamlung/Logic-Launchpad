
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Question, SubmitRecord, TestCase
import os

class Command(BaseCommand):
    help = 'Remove unused files from the file storage'

    def handle(self, *args, **kwargs):
        self.stdout.write('Scanning for unused files...')

        media_root = settings.MEDIA_ROOT

        # Define directories to scan
        directories = {
            'code_templates': Question.objects.values_list('start_code_template_file', flat=True),
            'answers': SubmitRecord.objects.values_list('answer', flat=True),
            'test_cases': TestCase.objects.values_list('input', flat=True).union(
                TestCase.objects.values_list('output', flat=True)
            )
        }

        for dir_name, used_files_query in directories.items():
            # Get the full path of the directory
            dir_path = os.path.join(media_root, dir_name)

            # Get all files in the directory
            all_files = set(os.listdir(dir_path))

            # Get files used in the database and convert them to a relative path
            used_files = set(os.path.relpath(file, media_root) for file in used_files_query if file)

            # Find unused files
            unused_files = all_files - used_files

            # Remove unused files
            for filename in unused_files:
                file_path = os.path.join(dir_path, filename)
                # os.remove(file_path)
                self.stdout.write(f'Removed: {file_path}')

        self.stdout.write('Unused files removal complete.')