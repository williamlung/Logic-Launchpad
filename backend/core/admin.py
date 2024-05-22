from django.contrib import admin
from .models import Question, SubmitRecord, TestCase, CustomUser, QuestionQuota

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Question)
admin.site.register(QuestionQuota)
admin.site.register(SubmitRecord)
admin.site.register(TestCase)

