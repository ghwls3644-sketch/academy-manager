from django.contrib import admin
from .models import NotificationTemplate, NotificationJob, NotificationLog, WeeklyReport


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'channel', 'trigger_type', 'auto_send', 'is_active']
    list_filter = ['channel', 'trigger_type', 'auto_send', 'is_active']
    search_fields = ['name', 'code', 'content']


@admin.register(NotificationJob)
class NotificationJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'target_type', 'total_count', 'success_count', 'created_at']
    list_filter = ['status', 'target_type']
    search_fields = ['subject', 'content']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_name', 'result', 'sent_at']
    list_filter = ['result']
    search_fields = ['recipient_name', 'recipient_contact']
    readonly_fields = ['sent_at']
