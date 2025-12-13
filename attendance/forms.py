from django import forms
from .models import Attendance
from students.models import Student
from classes.models import Class


class AttendanceForm(forms.ModelForm):
    """출결 등록/수정 폼"""
    
    class Meta:
        model = Attendance
        fields = ['student', 'assigned_class', 'date', 'status', 'note']
        labels = {
            'student': '학생',
            'assigned_class': '반',
            'date': '날짜',
            'status': '출결 상태',
            'note': '메모',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='enrolled')
        self.fields['assigned_class'].queryset = Class.objects.filter(is_active=True)


class BulkAttendanceForm(forms.Form):
    """일괄 출결 입력 폼"""
    assigned_class = forms.ModelChoiceField(
        label='반',
        queryset=Class.objects.filter(is_active=True),
        required=True
    )
    date = forms.DateField(
        label='날짜',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
