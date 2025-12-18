from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ParentAccount, ParentInvite, ParentMessage


class ParentRegistrationForm(UserCreationForm):
    """학부모 회원가입 폼"""
    invite_code = forms.CharField(
        label='초대 코드',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '초대 코드 입력'})
    )
    
    name = forms.CharField(
        label='이름',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        label='연락처',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '010-0000-0000'})
    )
    
    email = forms.EmailField(
        label='이메일',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    relationship = forms.CharField(
        label='관계',
        max_length=20,
        initial='부모',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '예: 어머니, 아버지'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class ParentLoginForm(forms.Form):
    """학부모 로그인 폼"""
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ParentMessageForm(forms.ModelForm):
    """학부모 메시지 폼"""
    class Meta:
        model = ParentMessage
        fields = ['student', 'subject', 'content']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class ParentProfileForm(forms.ModelForm):
    """학부모 프로필 수정 폼"""
    class Meta:
        model = ParentAccount
        fields = ['name', 'phone', 'email', 'relationship',
                  'receive_attendance_alert', 'receive_payment_alert', 'receive_score_alert']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'receive_attendance_alert': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_payment_alert': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_score_alert': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
