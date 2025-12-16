from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import MessageLog, Notification, SystemSetting, Backup


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['message_type', 'recipient', 'status', 'sent_at', 'created_at']
    list_filter = ['message_type', 'status', 'created_at']
    search_fields = ['recipient', 'recipient_phone', 'content']
    readonly_fields = ['created_at', 'sent_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']


@admin.register(SystemSetting)
class SystemSettingAdmin(SimpleHistoryAdmin):
    list_display = ['key', 'value', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['key', 'value', 'description']


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ['filename', 'status', 'file_size', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'completed_at']
