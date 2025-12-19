from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
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
    
    # 최근 알림 발송 (notifications 앱)
    recent_notifications = []
    try:
        from notifications.models import NotificationJob
        recent_notifications = NotificationJob.objects.order_by('-created_at')[:5]
    except:
        pass
    
    # 오늘 일정 (schedule 앱)
    today_events = []
    try:
        from schedule.models import CalendarEvent
        today_events = CalendarEvent.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        )[:5]
    except:
        pass
    
    # 최근 시험 (academics 앱)
    recent_exams = []
    try:
        from academics.models import Exam
        recent_exams = Exam.objects.order_by('-exam_date')[:3]
    except:
        pass
    
    context = {
        'student_stats': student_stats,
        'class_stats': class_stats,
        'attendance_stats': attendance_stats,
        'payment_stats': payment_stats,
        'recent_students': recent_students,
        'unpaid_payments': unpaid_payments,
        'absent_today': absent_today,
        'recent_notifications': recent_notifications,
        'today_events': today_events,
        'recent_exams': recent_exams,
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


@login_required
def dashboard_pdf(request):
    """대시보드 PDF 내보내기"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    
    # 통계 데이터 수집
    student_stats = {
        'total': Student.objects.count(),
        'enrolled': Student.objects.filter(status='enrolled').count(),
        'paused': Student.objects.filter(status='paused').count(),
        'withdrawn': Student.objects.filter(status='withdrawn').count(),
    }
    
    class_stats = {
        'total': Class.objects.filter(is_active=True).count(),
    }
    
    today_attendance = Attendance.objects.filter(date=today)
    attendance_stats = {
        'present': today_attendance.filter(status='present').count(),
        'absent': today_attendance.filter(status='absent').count(),
        'late': today_attendance.filter(status='late').count(),
    }
    
    payment_stats = Payment.objects.filter(year=current_year, month=current_month).aggregate(
        total=Sum('amount'),
        paid=Sum('paid_amount')
    )
    payment_stats['total'] = payment_stats['total'] or 0
    payment_stats['paid'] = payment_stats['paid'] or 0
    payment_stats['unpaid'] = payment_stats['total'] - payment_stats['paid']
    
    unpaid_payments = Payment.objects.filter(
        year=current_year,
        month=current_month,
        status__in=['unpaid', 'partial']
    ).select_related('student').order_by('-amount')[:10]
    
    # PDF 생성
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    
    # 제목
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
    )
    elements.append(Paragraph(f"Academy Manager - Dashboard Report", title_style))
    elements.append(Paragraph(f"{today.strftime('%Y년 %m월 %d일')} 현황", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # 학생 통계 테이블
    elements.append(Paragraph("학생 현황", styles['Heading2']))
    student_data = [
        ['구분', '인원'],
        ['재원', f"{student_stats['enrolled']}명"],
        ['휴원', f"{student_stats['paused']}명"],
        ['퇴원', f"{student_stats['withdrawn']}명"],
        ['전체', f"{student_stats['total']}명"],
    ]
    student_table = Table(student_data, colWidths=[80*mm, 80*mm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))
    
    # 출결 통계
    elements.append(Paragraph("오늘 출결 현황", styles['Heading2']))
    attendance_data = [
        ['출석', '결석', '지각'],
        [f"{attendance_stats['present']}명", f"{attendance_stats['absent']}명", f"{attendance_stats['late']}명"],
    ]
    attendance_table = Table(attendance_data, colWidths=[53*mm, 53*mm, 53*mm])
    attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(attendance_table)
    elements.append(Spacer(1, 20))
    
    # 수납 통계
    elements.append(Paragraph(f"{current_month}월 수납 현황", styles['Heading2']))
    payment_data = [
        ['청구액', '납부액', '미납액'],
        [f"{payment_stats['total']:,}원", f"{payment_stats['paid']:,}원", f"{payment_stats['unpaid']:,}원"],
    ]
    payment_table = Table(payment_data, colWidths=[53*mm, 53*mm, 53*mm])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4285f4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 20))
    
    # 미납자 목록
    if unpaid_payments:
        elements.append(Paragraph("미납자 목록", styles['Heading2']))
        unpaid_data = [['학생명', '기간', '미납액']]
        for p in unpaid_payments:
            unpaid_data.append([
                p.student.name,
                f"{p.year}년 {p.month}월",
                f"{p.remaining_amount:,}원"
            ])
        unpaid_table = Table(unpaid_data, colWidths=[60*mm, 50*mm, 50*mm])
        unpaid_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(unpaid_table)
    
    # PDF 빌드
    doc.build(elements)
    
    # 응답 생성
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dashboard_report_{today.strftime("%Y%m%d")}.pdf"'
    return response

