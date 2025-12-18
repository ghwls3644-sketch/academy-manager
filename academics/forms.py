from django import forms
from .models import Subject, Exam, Score, LearningGoal, ReportCard
from students.models import Student
from classes.models import Class


class SubjectForm(forms.ModelForm):
    """과목 폼"""
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExamForm(forms.ModelForm):
    """시험 폼"""
    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'subject', 'assigned_class', 'exam_date', 'max_score', 'description', 'is_published']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'assigned_class': forms.Select(attrs={'class': 'form-select'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ScoreForm(forms.ModelForm):
    """성적 입력 폼"""
    class Meta:
        model = Score
        fields = ['student', 'score', 'grade', 'feedback']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ScoreBulkForm(forms.Form):
    """성적 일괄 입력용"""
    def __init__(self, students, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for student in students:
            self.fields[f'score_{student.id}'] = forms.DecimalField(
                label=student.name,
                required=False,
                max_digits=5,
                decimal_places=1,
                widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.1'})
            )


class LearningGoalForm(forms.ModelForm):
    """학습 목표 폼"""
    class Meta:
        model = LearningGoal
        fields = ['student', 'subject', 'title', 'description', 'target_score', 'start_date', 'end_date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ReportCardForm(forms.ModelForm):
    """성적표 폼"""
    class Meta:
        model = ReportCard
        fields = ['student', 'period_type', 'period_start', 'period_end', 'title', 'teacher_comment']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'period_type': forms.Select(attrs={'class': 'form-select'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
