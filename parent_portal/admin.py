from django.contrib import admin
from .models import ParentAccount, ParentInvite, ParentMessage


@admin.register(ParentAccount)
class ParentAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'relationship', 'is_active', 'last_login_at']
    list_filter = ['is_active', 'receive_attendance_alert', 'receive_payment_alert']
    search_fields = ['name', 'phone', 'email']
    filter_horizontal = ['children']


@admin.register(ParentInvite)
class ParentInviteAdmin(admin.ModelAdmin):
    list_display = ['student', 'code', 'status', 'expires_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__name', 'code']


@admin.register(ParentMessage)
class ParentMessageAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'subject', 'direction', 'is_read', 'created_at']
    list_filter = ['direction', 'is_read']
    search_fields = ['parent__name', 'subject', 'content']
