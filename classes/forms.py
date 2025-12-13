from django import forms
from .models import Class
from teachers.models import Teacher


class ClassForm(forms.ModelForm):
    """반 등록/수정 폼"""
    
    # 수업 요일 체크박스
    WEEKDAY_CHOICES = [
        ('mon', '월'),
        ('tue', '화'),
        ('wed', '수'),
        ('thu', '목'),
        ('fri', '금'),
        ('sat', '토'),
        ('sun', '일'),
    ]
    weekdays_list = forms.MultipleChoiceField(
        label='수업 요일',
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Class
        fields = [
            'name', 'teacher', 'subject', 'description',
            'start_time', 'end_time', 'max_students', 'monthly_fee', 'is_active'
        ]
        labels = {
            'name': '반 이름',
            'teacher': '담당 강사',
            'subject': '과목',
            'description': '설명',
            'start_time': '시작 시간',
            'end_time': '종료 시간',
            'max_students': '정원',
            'monthly_fee': '월 수강료',
            'is_active': '활성화',
        }
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
        
        if self.instance and self.instance.pk and self.instance.weekdays:
            self.fields['weekdays_list'].initial = self.instance.weekdays.split(',')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        weekdays = self.cleaned_data.get('weekdays_list', [])
        instance.weekdays = ','.join(weekdays)
        if commit:
            instance.save()
        return instance
