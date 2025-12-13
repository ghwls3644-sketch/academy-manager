from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'assigned_class', 'status', 'phone', 'parent_phone', 'enrollment_date']
    list_filter = ['status', 'assigned_class', 'gender']
    search_fields = ['name', 'phone', 'parent_name', 'parent_phone']
    raw_id_fields = ['assigned_class']
    date_hierarchy = 'enrollment_date'
