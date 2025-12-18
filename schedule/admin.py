from django.contrib import admin
from .models import CalendarEvent, MakeupClass, HolidayRange


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'start_time', 'assigned_class', 'teacher']
    list_filter = ['event_type', 'start_date', 'assigned_class']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'


@admin.register(MakeupClass)
class MakeupClassAdmin(admin.ModelAdmin):
    list_display = ['original_class', 'original_date', 'status', 'created_at']
    list_filter = ['status', 'original_date']
    search_fields = ['original_class__name', 'reason']


@admin.register(HolidayRange)
class HolidayRangeAdmin(admin.ModelAdmin):
    list_display = ['title', 'holiday_type', 'start_date', 'end_date', 'affects_all']
    list_filter = ['holiday_type', 'affects_all']
    search_fields = ['title', 'description']
    filter_horizontal = ['affected_classes']
