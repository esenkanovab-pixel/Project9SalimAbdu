# lms/forms.py

from django import forms
from .models import Course, Lesson, Student, HomeworkSubmission

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'teacher']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'content', 'materials']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'courses']

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['file', 'comment']