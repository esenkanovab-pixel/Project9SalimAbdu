# lms/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def dict_list_course(certificates, course):
    """Проверяет, существует ли сертификат для данного курса в списке сертификатов."""
    return certificates.filter(course=course).exists()