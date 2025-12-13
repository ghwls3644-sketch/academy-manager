from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee', 'subject', 'is_active', 'created_at']
    list_filter = ['is_active', 'subject']
    search_fields = ['employee__user__username', 'employee__user__first_name', 'subject']
    raw_id_fields = ['employee']
