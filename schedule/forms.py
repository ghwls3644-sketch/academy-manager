from django import forms
from .models import CalendarEvent, MakeupClass, HolidayRange
from classes.models import Class
from teachers.models import Teacher


class CalendarEventForm(forms.ModelForm):
    """캘린더 이벤트 폼"""
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'event_type', 'description',
            'start_date', 'end_date', 'start_time', 'end_time', 'all_day',
            'assigned_class', 'teacher', 'location', 'color'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assigned_class': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }


class MakeupClassForm(forms.ModelForm):
    """보강 수업 폼"""
    class Meta:
        model = MakeupClass
        fields = ['original_date', 'original_class', 'reason']
        widgets = {
            'original_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'original_class': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class HolidayRangeForm(forms.ModelForm):
    """휴원 기간 폼"""
    class Meta:
        model = HolidayRange
        fields = [
            'title', 'holiday_type', 'start_date', 'end_date',
            'description', 'affects_all', 'affected_classes', 'notify_parents'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'holiday_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'affects_all': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'affected_classes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'notify_parents': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
