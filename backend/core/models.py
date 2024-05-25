from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass

class Question(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    week = models.IntegerField(default=1)
    start_code_template_file = models.FileField(upload_to='code_templates')

class QuestionQuota(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    quota = models.IntegerField(default=80)
    passed = models.BooleanField(default=False)

class SubmitRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.FileField(upload_to='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    
class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    input = models.FileField(upload_to='test_cases')
    output = models.FileField(upload_to='test_cases')
    hidden = models.BooleanField(default=False)