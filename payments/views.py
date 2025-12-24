from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Payment
from .forms import PaymentForm
from students.models import Student
from core.utils import get_year_choices


@login_required
def payment_list(request):
    """수납 목록"""
    payments = Payment.objects.select_related('student', 'student__assigned_class').all()
    
    # 년/월 필터
    year = request.GET.get('year', str(timezone.now().year))
    month = request.GET.get('month', '')
    
    if year:
        payments = payments.filter(year=year)
    if month:
        payments = payments.filter(month=month)
    
    # 상태 필터
    status = request.GET.get('status', '')
    if status:
        payments = payments.filter(status=status)
    
    # 학생 필터
    student_id = request.GET.get('student', '')
    if student_id:
        payments = payments.filter(student_id=student_id)
    
    # 통계
    stats = payments.aggregate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount')
    )
    stats['total_amount'] = stats['total_amount'] or 0
    stats['total_paid'] = stats['total_paid'] or 0
    stats['total_unpaid'] = stats['total_amount'] - stats['total_paid']
    
    status_counts = payments.values('status').annotate(count=Count('id'))
    stats['paid_count'] = next((s['count'] for s in status_counts if s['status'] == 'paid'), 0)
    stats['unpaid_count'] = next((s['count'] for s in status_counts if s['status'] == 'unpaid'), 0)
    stats['partial_count'] = next((s['count'] for s in status_counts if s['status'] == 'partial'), 0)
    
    # 정렬 및 페이지네이션
    payments = payments.order_by('-year', '-month', '-payment_date')
    paginator = Paginator(payments, 20)
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)
    
    # 년도 목록 - 유틸 함수 사용
    years = get_year_choices()
    
    return render(request, 'payments/payment_list.html', {
        'payments': payments,
        'stats': stats,
        'years': years,
        'year': year,
        'month': month,
        'status': status,
        'student_id': student_id,
    })


@login_required
def payment_create(request):
    """수납 등록"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '수납이 등록되었습니다.')
            return redirect('payments:list')
    else:
        initial = {
            'year': timezone.now().year,
            'month': timezone.now().month,
            'payment_date': timezone.now().date()
        }
        form = PaymentForm(initial=initial)
    
    return render(request, 'payments/payment_form.html', {
        'form': form,
        'title': '수납 등록',
    })


@login_required
def payment_update(request, pk):
    """수납 수정"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, '수납 정보가 수정되었습니다.')
            return redirect('payments:list')
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'payments/payment_form.html', {
        'form': form,
        'payment': payment,
        'title': '수납 수정',
    })


@login_required
def payment_delete(request, pk):
    """수납 삭제"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, '수납 기록이 삭제되었습니다.')
        return redirect('payments:list')
    
    return render(request, 'payments/payment_confirm_delete.html', {
        'payment': payment,
    })


@login_required
def unpaid_list(request):
    """미납자 목록"""
    year = request.GET.get('year', str(timezone.now().year))
    month = request.GET.get('month', str(timezone.now().month))
    
    payments = Payment.objects.select_related('student').filter(
        year=year,
        month=month,
        status__in=['unpaid', 'partial']
    ).order_by('student__name')
    
    years = get_year_choices()
    
    return render(request, 'payments/unpaid_list.html', {
        'payments': payments,
        'years': years,
        'year': year,
        'month': month,
    })
