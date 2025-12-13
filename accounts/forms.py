from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Employee


class LoginForm(AuthenticationForm):
    """로그인 폼"""
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '아이디를 입력하세요',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '비밀번호를 입력하세요',
        })
    )


class ProfileForm(forms.ModelForm):
    """프로필 수정 폼"""
    first_name = forms.CharField(label='이름', max_length=30, required=False)
    last_name = forms.CharField(label='성', max_length=30, required=False)
    email = forms.EmailField(label='이메일', required=False)
    
    class Meta:
        model = Employee
        fields = ['phone', 'profile_image']
        labels = {
            'phone': '연락처',
            'profile_image': '프로필 이미지',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        user = employee.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            employee.save()
        return employee
