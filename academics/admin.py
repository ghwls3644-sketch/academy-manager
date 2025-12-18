from django.contrib import admin
from .models import Subject, Exam, Score, LearningGoal, ReportCard


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'assigned_class', 'exam_date', 'max_score', 'is_published']
    list_filter = ['exam_type', 'subject', 'is_published', 'exam_date']
    search_fields = ['name']
    date_hierarchy = 'exam_date'


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'score', 'grade', 'rank', 'created_at']
    list_filter = ['exam', 'grade']
    search_fields = ['student__name', 'exam__name']
    raw_id_fields = ['student', 'exam']


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'subject', 'target_score', 'current_progress', 'status', 'end_date']
    list_filter = ['status', 'subject']
    search_fields = ['student__name', 'title']


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'period_type', 'period_start', 'period_end', 'is_published']
    list_filter = ['period_type', 'is_published']
    search_fields = ['student__name', 'title']
