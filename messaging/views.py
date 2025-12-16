"""
알림 발송 뷰
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from students.models import Student
from classes.models import Class
from payments.models import Payment
from core.models import MessageLog


@login_required
def message_send(request):
    """알림 발송 페이지"""
    classes = Class.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # 폼 데이터
        message_type = request.POST.get('message_type', 'sms')
        target_type = request.POST.get('target_type')
        class_id = request.POST.get('class_id')
        student_ids = request.POST.getlist('student_ids')
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, '메시지 내용을 입력해주세요.')
            return redirect('messaging:send')
        
        # 대상 학생 선택
        students = []
        
        if target_type == 'class' and class_id:
            students = Student.objects.filter(
                assigned_class_id=class_id,
                status='enrolled'
            )
        elif target_type == 'students' and student_ids:
            students = Student.objects.filter(id__in=student_ids)
        elif target_type == 'unpaid':
            # 미납자
            current_year = timezone.now().year
            current_month = timezone.now().month
            unpaid_payments = Payment.objects.filter(
                year=current_year,
                month=current_month,
                status__in=['unpaid', 'partial']
            ).values_list('student_id', flat=True)
            students = Student.objects.filter(id__in=unpaid_payments, status='enrolled')
        elif target_type == 'all':
            students = Student.objects.filter(status='enrolled')
        
        # 메시지 로그 생성
        sent_count = 0
        for student in students:
            phone = student.parent_phone or student.phone
            if phone:
                MessageLog.objects.create(
                    message_type=message_type,
                    recipient=student.name,
                    recipient_phone=phone,
                    content=content,
                    status='sent',  # 실제로는 'pending' 후 비동기 처리
                    sent_at=timezone.now(),
                    created_by=request.user
                )
                sent_count += 1
        
        if sent_count > 0:
            messages.success(request, f'{sent_count}명에게 메시지가 발송되었습니다.')
        else:
            messages.warning(request, '발송 대상이 없습니다.')
        
        return redirect('messaging:logs')
    
    # 학생 목록 (개별 선택용)
    students = Student.objects.filter(status='enrolled').order_by('name')
    
    return render(request, 'messaging/send.html', {
        'classes': classes,
        'students': students,
    })


@login_required
def message_logs(request):
    """발송 로그 페이지"""
    logs = MessageLog.objects.select_related('created_by').order_by('-created_at')
    
    # 필터
    message_type = request.GET.get('message_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if message_type:
        logs = logs.filter(message_type=message_type)
    if status:
        logs = logs.filter(status=status)
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'messaging/logs.html', {
        'page_obj': page_obj,
        'selected_type': message_type,
        'selected_status': status,
    })
