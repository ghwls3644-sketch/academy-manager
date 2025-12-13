from django import forms
from .models import Student
from classes.models import Class


class StudentForm(forms.ModelForm):
    """학생 등록/수정 폼"""
    
    class Meta:
        model = Student
        fields = [
            'name', 'gender', 'birth_date', 'phone',
            'parent_name', 'parent_phone', 'parent_relation',
            'assigned_class', 'status', 'enrollment_date', 'withdrawal_date',
            'school_name', 'grade', 'note'
        ]
        labels = {
            'name': '이름',
            'gender': '성별',
            'birth_date': '생년월일',
            'phone': '연락처',
            'parent_name': '학부모 이름',
            'parent_phone': '학부모 연락처',
            'parent_relation': '관계',
            'assigned_class': '반',
            'status': '재원 상태',
            'enrollment_date': '등록일',
            'withdrawal_date': '퇴원일',
            'school_name': '학교명',
            'grade': '학년',
            'note': '메모',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'withdrawal_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_class'].queryset = Class.objects.filter(is_active=True)


class StudentSearchForm(forms.Form):
    """학생 검색 폼"""
    search = forms.CharField(label='검색', required=False)
    status = forms.ChoiceField(
        label='상태',
        choices=[('', '전체')] + list(Student.STATUS_CHOICES),
        required=False
    )
    assigned_class = forms.ModelChoiceField(
        label='반',
        queryset=Class.objects.filter(is_active=True),
        required=False,
        empty_label='전체'
    )
