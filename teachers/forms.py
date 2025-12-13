from django import forms
from django.contrib.auth.models import User
from accounts.models import Employee, Role
from .models import Teacher


class TeacherForm(forms.ModelForm):
    """강사 등록/수정 폼"""
    # User 필드
    username = forms.CharField(label='아이디', max_length=150)
    password = forms.CharField(
        label='비밀번호', 
        widget=forms.PasswordInput, 
        required=False,
        help_text='수정 시 비밀번호를 입력하지 않으면 기존 비밀번호가 유지됩니다.'
    )
    first_name = forms.CharField(label='이름', max_length=30)
    last_name = forms.CharField(label='성', max_length=30, required=False)
    email = forms.EmailField(label='이메일', required=False)
    
    # Employee 필드
    phone = forms.CharField(label='연락처', max_length=20, required=False)
    hire_date = forms.DateField(
        label='입사일', 
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Teacher
        fields = ['subject', 'bio', 'is_active']
        labels = {
            'subject': '담당 과목',
            'bio': '소개',
            'is_active': '활성 여부',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            employee = self.instance.employee
            user = employee.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = employee.phone
            self.fields['hire_date'].initial = employee.hire_date
            self.fields['username'].widget.attrs['readonly'] = True
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if not self.instance.pk:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('이미 사용중인 아이디입니다.')
        return username
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        if self.instance.pk:
            # Update existing
            employee = self.instance.employee
            user = employee.user
        else:
            # Create new
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'] or 'defaultpassword123'
            )
            role, _ = Role.objects.get_or_create(name='teacher')
            employee = Employee.objects.create(user=user, role=role)
            teacher.employee = employee
        
        # Update user fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        user.save()
        
        # Update employee fields
        employee.phone = self.cleaned_data['phone']
        employee.hire_date = self.cleaned_data['hire_date']
        employee.save()
        
        if commit:
            teacher.save()
        return teacher
