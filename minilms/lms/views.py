# lms/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.conf import settings
import io
from django.core.files.base import ContentFile
from .models import Course, Student, Lesson, HomeworkSubmission, Certificate
from .forms import CourseForm, StudentForm, HomeworkForm, LessonForm


# Курсы (Course)
def courses_list(request):
    """Список курсов - домашняя страница"""
    courses = Course.objects.order_by('-created_at')
    return render(request, 'lms/course_list.html', {'courses': courses})

def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс успешно создан.')
            return redirect('lms:courses_list')
    else:
        form = CourseForm()
    return render(request, 'lms/course_form.html', {'form': form})

def course_edit(request, pk):
    c = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс обновлён.')
            return redirect('lms:courses_list')
    else:
        form = CourseForm(instance=c)
    return render(request, 'lms/course_form.html', {'form': form, 'course': c})


# Студенты (Student)
def students_list(request):
    students = Student.objects.order_by('-created_at')
    return render(request, 'lms/student_list.html', {'students': students})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Студент добавлен.')
            return redirect('lms:students_list')
    else:
        form = StudentForm()
    return render(request, 'lms/student_form.html', {'form': form})


# Уроки (Lesson)
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'lms/lesson_detail.html', {'lesson': lesson})

def lesson_create(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save()
            
            # Уведомление студентов по email
            students = lesson.course.students.all()
            recipients = [s.email for s in students if s.email]
            if recipients:
                send_mail(
                    subject=f'Новый урок в курсе {lesson.course.title}: {lesson.title}',
                    message=f'Добавлен новый урок: {lesson.title}. Подробности: {request.build_absolute_uri(reverse("lms:lesson_detail", args=[lesson.pk]))}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    fail_silently=True
                )
            messages.success(request, 'Урок добавлен и студенты уведомлены.')
            return redirect('lms:courses_list')
    else:
        form = LessonForm()
    return render(request, 'lms/lesson_form.html', {'form': form})


# Домашнее задание (Homework)
def homework_submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    students = Student.objects.filter(courses__in=[lesson.course]) # Фильтруем студентов по курсу
    
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES)
        student_id = request.POST.get('student_id')
        
        try:
            student = get_object_or_404(Student, pk=student_id)
        except:
            messages.error(request, 'Ошибка: Студент не найден.')
            return redirect('lms:lesson_detail', pk=lesson.pk)
        
        if form.is_valid():
            hw = form.save(commit=False)
            hw.lesson = lesson
            hw.student = student
            hw.save()
            
            # Уведомление преподавателя
            send_mail(
                subject=f'Новая домашняя работа от {student.name}',
                message=f'Домашнее задание для урока {lesson.title} отправлено.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL], # Отправляем на почту по умолчанию (консоль)
                fail_silently=True
            )
            messages.success(request, 'Домашнее задание успешно отправлено.')
            return redirect('lms:lesson_detail', pk=lesson.pk)
    else:
        form = HomeworkForm()
    
    return render(request, 'lms/homework_submit.html', {'form': form, 'lesson': lesson, 'students': students})


# Сертификаты (Certificate)
def generate_certificate(request, course_id, student_id):
    course = get_object_or_404(Course, pk=course_id)
    student = get_object_or_404(Student, pk=student_id)

    # Проверка, не сгенерирован ли уже
    if Certificate.objects.filter(student=student, course=course).exists():
        messages.warning(request, 'Сертификат уже существует.')
        return redirect('lms:students_list')

    buffer = io.BytesIO()
    # Создаем PDF
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(300, 700, "CERTIFICATE OF COMPLETION")
    p.setFont("Helvetica", 18)
    p.drawCentredString(300, 650, f"This certifies that {student.name}")
    p.drawCentredString(300, 620, f"has successfully completed the course")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 590, f"{course.title}")
    p.setFont("Helvetica", 14)
    p.drawCentredString(300, 500, f"Issued on: {Certificate.objects.last().issued_at.strftime('%Y-%m-%d') if Certificate.objects.exists() else 'Today'}") # Простой костыль
    p.showPage()
    p.save()
    buffer.seek(0)

    # Сохраняем в базу данных
    cert_file = ContentFile(buffer.read())
    cert = Certificate.objects.create(student=student, course=course)
    cert.pdf.save(f"certificate_{student.id}_{course.id}.pdf", cert_file)
    messages.success(request, 'Сертификат сгенерирован и сохранен.')
    return redirect('lms:students_list')