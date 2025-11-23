# lms/admin.py

from django.contrib import admin
from .models import Course, Student, Lesson, HomeworkSubmission, Certificate

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Lesson)
admin.site.register(HomeworkSubmission)
admin.site.register(Certificate)