from django.contrib import admin
from .models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'subject', 'weekday_display', 'schedule_display', 'student_count', 'is_active']
    list_filter = ['is_active', 'subject']
    search_fields = ['name', 'subject', 'teacher__employee__user__first_name']
    raw_id_fields = ['teacher']
