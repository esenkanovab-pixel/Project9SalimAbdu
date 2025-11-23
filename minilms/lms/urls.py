# lms/urls.py

from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    # Курсы
    path('', views.courses_list, name='courses_list'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),

    # Студенты
    path('students/', views.students_list, name='students_list'),
    path('students/new/', views.student_create, name='student_create'),

    # Уроки
    path('lessons/new/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/submit/', views.homework_submit, name='homework_submit'),

    # Сертификаты
    path('certificates/<int:course_id>/<int:student_id>/generate/', views.generate_certificate, name='generate_certificate'),
]