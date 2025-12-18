from django import forms
from .models import NotificationTemplate, NotificationJob
from students.models import Student
from classes.models import Class


class NotificationTemplateForm(forms.ModelForm):
    """알림 템플릿 폼"""
    class Meta:
        model = NotificationTemplate
        fields = [
            'name', 'code', 'channel', 'trigger_type',
            'subject', 'content',
            'auto_send', 'days_before', 'send_time', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'channel': forms.Select(attrs={'class': 'form-select'}),
            'trigger_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'auto_send': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'days_before': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'send_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NotificationSendForm(forms.Form):
    """알림 발송 폼"""
    template = forms.ModelChoiceField(
        queryset=NotificationTemplate.objects.filter(is_active=True),
        label='템플릿',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    
    target_type = forms.ChoiceField(
        choices=NotificationJob.TARGET_TYPE_CHOICES,
        label='대상 유형',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    target_class = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        label='대상 반',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    
    target_students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(status='enrolled'),
        label='대상 학생',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        required=False
    )
    
    subject = forms.CharField(
        label='제목',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    content = forms.CharField(
        label='내용',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    scheduled_at = forms.DateTimeField(
        label='예약 발송일시',
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        required=False
    )
