from django import forms
from .models import Payment
from students.models import Student


class PaymentForm(forms.ModelForm):
    """수납 등록/수정 폼"""
    
    class Meta:
        model = Payment
        fields = ['student', 'year', 'month', 'amount', 'paid_amount', 'payment_method', 'payment_date', 'note']
        labels = {
            'student': '학생',
            'year': '년도',
            'month': '월',
            'amount': '청구 금액 (원)',
            'paid_amount': '납부 금액 (원)',
            'payment_method': '결제 방식',
            'payment_date': '납부일',
            'note': '메모',
        }
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='enrolled')
