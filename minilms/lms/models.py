# lms/models.py

from django.db import models
from django.urls import reverse

class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(blank=True, verbose_name="Описание")
    teacher = models.CharField(max_length=150, blank=True, verbose_name="Преподаватель")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Примечание: предполагается, что будет course_detail
        return reverse('lms:courses_list') 

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

class Student(models.Model):
    name = models.CharField(max_length=150, verbose_name="Имя")
    email = models.EmailField(unique=True, verbose_name="Email")
    courses = models.ManyToManyField(Course, related_name='students', blank=True, verbose_name="Записан на курсы")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    title = models.CharField(max_length=255, verbose_name="Название урока")
    content = models.TextField(blank=True, verbose_name="Содержимое")
    materials = models.FileField(upload_to='materials/', blank=True, null=True, verbose_name="Материалы")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Отправлено'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', verbose_name="Студент")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions', verbose_name="Урок")
    file = models.FileField(upload_to='homework/', verbose_name="Файл")
    comment = models.TextField(blank=True, verbose_name="Комментарий студента")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted', verbose_name="Статус")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ДЗ: {self.student.name} — {self.lesson.title}"

    class Meta:
        verbose_name = "Отправка Д/З"
        verbose_name_plural = "Отправки Д/З"

class Certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates', verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")
    pdf = models.FileField(upload_to='certificates/', verbose_name="Сертификат PDF")
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сертификат: {self.student.name} — {self.course.title}"

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"