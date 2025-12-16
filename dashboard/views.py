from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from students.models import Student
from classes.models import Class
from attendance.models import Attendance
from payments.models import Payment


@login_required
def dashboard_index(request):
    """관리자 대시보드"""
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    
    # 학생 통계
    student_stats = {
        'total': Student.objects.count(),
        'enrolled': Student.objects.filter(status='enrolled').count(),
        'paused': Student.objects.filter(status='paused').count(),
        'withdrawn': Student.objects.filter(status='withdrawn').count(),
    }
    
    # 반 통계
    class_stats = {
        'total': Class.objects.filter(is_active=True).count(),
    }
    
    # 오늘 출결 통계
    today_attendance = Attendance.objects.filter(date=today)
    attendance_stats = {
        'present': today_attendance.filter(status='present').count(),
        'absent': today_attendance.filter(status='absent').count(),
        'late': today_attendance.filter(status='late').count(),
    }
    
    # 이번 달 수납 통계
    payment_stats = Payment.objects.filter(year=current_year, month=current_month).aggregate(
        total=Sum('amount'),
        paid=Sum('paid_amount')
    )
    payment_stats['total'] = payment_stats['total'] or 0
    payment_stats['paid'] = payment_stats['paid'] or 0
    payment_stats['unpaid'] = payment_stats['total'] - payment_stats['paid']
    payment_stats['unpaid_count'] = Payment.objects.filter(
        year=current_year, 
        month=current_month,
        status__in=['unpaid', 'partial']
    ).count()
    
    # 최근 등록 학생 (5명)
    recent_students = Student.objects.order_by('-created_at')[:5]
    
    # 미납자 목록 (상위 5명)
    unpaid_payments = Payment.objects.filter(
        year=current_year,
        month=current_month,
        status__in=['unpaid', 'partial']
    ).select_related('student').order_by('-amount')[:5]
    
    # 오늘 결석 학생
    absent_today = Attendance.objects.filter(
        date=today,
        status='absent'
    ).select_related('student')[:5]
    
    context = {
        'student_stats': student_stats,
        'class_stats': class_stats,
        'attendance_stats': attendance_stats,
        'payment_stats': payment_stats,
        'recent_students': recent_students,
        'unpaid_payments': unpaid_payments,
        'absent_today': absent_today,
        'current_year': current_year,
        'current_month': current_month,
        'today': today,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def dashboard_attendance_api(request):
    """출석률 API for Chart.js"""
    from django.http import JsonResponse
    from calendar import monthrange
    
    # 최근 6개월 데이터
    today = timezone.now().date()
    months = []
    rates = []
    
    for i in range(5, -1, -1):
        # i개월 전
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        # 해당 월 출결 데이터
        total = Attendance.objects.filter(
            date__year=target_year,
            date__month=target_month
        ).count()
        present = Attendance.objects.filter(
            date__year=target_year,
            date__month=target_month,
            status='present'
        ).count()
        
        rate = round((present / total * 100) if total > 0 else 0, 1)
        
        months.append(f"{target_month}월")
        rates.append(rate)
    
    return JsonResponse({
        'labels': months,
        'data': rates,
    })


@login_required
def dashboard_revenue_api(request):
    """매출 API for Chart.js"""
    from django.http import JsonResponse
    
    # 최근 6개월 데이터
    today = timezone.now().date()
    months = []
    revenues = []
    
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        # 해당 월 수납 데이터
        total = Payment.objects.filter(
            year=target_year,
            month=target_month
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        
        months.append(f"{target_month}월")
        revenues.append(total)
    
    return JsonResponse({
        'labels': months,
        'data': revenues,
    })
