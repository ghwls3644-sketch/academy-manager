from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'assigned_class', 'date', 'status', 'note']
    list_filter = ['status', 'assigned_class', 'date']
    search_fields = ['student__name', 'note']
    date_hierarchy = 'date'
    raw_id_fields = ['student', 'assigned_class']
