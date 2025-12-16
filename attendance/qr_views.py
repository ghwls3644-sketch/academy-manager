"""
QR 출석 관련 뷰
"""
import secrets
import qrcode
import io
import base64
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import IntegrityError

from classes.models import Class
from students.models import Student
from .models import Attendance, QrSession, QrScanLog


@login_required
def qr_generate(request):
    """QR 코드 생성 페이지"""
    classes = Class.objects.filter(is_active=True)
    qr_image = None
    session = None
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        expiry_seconds = int(request.POST.get('expiry_seconds', 120))
        
        assigned_class = get_object_or_404(Class, id=class_id)
        
        # 기존 활성 세션 종료
        QrSession.objects.filter(
            assigned_class=assigned_class,
            status='active'
        ).update(status='closed')
        
        # 새 세션 생성
        now = timezone.now()
        token = secrets.token_urlsafe(32)
        
        session = QrSession.objects.create(
            assigned_class=assigned_class,
            lesson_date=now.date(),
            token=token,
            starts_at=now,
            expires_at=now + timedelta(seconds=expiry_seconds),
            created_by=request.user
        )
        
        # QR 코드 생성
        qr_url = request.build_absolute_uri(f'/attendance/qr/scan/?token={token}')
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'attendance/qr_generate.html', {
        'classes': classes,
        'qr_image': qr_image,
        'session': session,
    })


@login_required
def qr_scan(request):
    """QR 스캔 페이지 (학생용)"""
    token = request.GET.get('token', '')
    session = None
    error = None
    
    if token:
        try:
            session = QrSession.objects.get(token=token)
            session.check_and_expire()
            if session.status != 'active':
                error = '만료된 QR 코드입니다.'
        except QrSession.DoesNotExist:
            error = '유효하지 않은 QR 코드입니다.'
    
    # 해당 반의 학생 목록
    students = []
    if session and session.status == 'active':
        students = Student.objects.filter(
            assigned_class=session.assigned_class,
            status='enrolled'
        ).order_by('name')
    
    return render(request, 'attendance/qr_scan.html', {
        'token': token,
        'session': session,
        'students': students,
        'error': error,
    })


@csrf_exempt
@require_POST
def qr_scan_api(request):
    """QR 스캔 처리 API"""
    import json
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    
    token = data.get('token')
    student_id = data.get('student_id')
    
    # 클라이언트 정보
    client_ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    # 세션 확인
    try:
        session = QrSession.objects.get(token=token)
    except QrSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '유효하지 않은 QR 코드입니다.',
            'reason': 'invalid_token'
        })
    
    session.check_and_expire()
    
    if session.status != 'active':
        QrScanLog.objects.create(
            qr_session=session,
            result='fail',
            fail_reason='expired',
            client_ip=client_ip,
            user_agent=user_agent
        )
        return JsonResponse({
            'success': False,
            'error': '만료된 QR 코드입니다.',
            'reason': 'expired'
        })
    
    # 학생 확인
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        QrScanLog.objects.create(
            qr_session=session,
            result='fail',
            fail_reason='not_enrolled',
            client_ip=client_ip,
            user_agent=user_agent
        )
        return JsonResponse({
            'success': False,
            'error': '학생을 찾을 수 없습니다.',
            'reason': 'not_enrolled'
        })
    
    # 해당 반 학생인지 확인
    if student.assigned_class_id != session.assigned_class_id:
        QrScanLog.objects.create(
            qr_session=session,
            student=student,
            result='fail',
            fail_reason='not_enrolled',
            client_ip=client_ip,
            user_agent=user_agent
        )
        return JsonResponse({
            'success': False,
            'error': '해당 반에 등록되지 않은 학생입니다.',
            'reason': 'not_enrolled'
        })
    
    # 중복 출석 확인
    existing = Attendance.objects.filter(
        student=student,
        date=session.lesson_date
    ).exists()
    
    if existing:
        QrScanLog.objects.create(
            qr_session=session,
            student=student,
            result='fail',
            fail_reason='duplicate',
            client_ip=client_ip,
            user_agent=user_agent
        )
        return JsonResponse({
            'success': False,
            'error': '이미 출석 처리되었습니다.',
            'reason': 'duplicate'
        })
    
    # 출석 처리
    try:
        Attendance.objects.create(
            student=student,
            assigned_class=session.assigned_class,
            date=session.lesson_date,
            status='present',
            note='QR 출석'
        )
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'error': '이미 출석 처리되었습니다.',
            'reason': 'duplicate'
        })
    
    # 성공 로그
    QrScanLog.objects.create(
        qr_session=session,
        student=student,
        result='success',
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{student.name}님 출석이 완료되었습니다!'
    })


@login_required
def qr_logs(request):
    """QR 스캔 로그 페이지"""
    logs = QrScanLog.objects.select_related('qr_session', 'student', 'qr_session__assigned_class')
    
    # 필터
    class_id = request.GET.get('class_id')
    result = request.GET.get('result')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if class_id:
        logs = logs.filter(qr_session__assigned_class_id=class_id)
    if result:
        logs = logs.filter(result=result)
    if date_from:
        logs = logs.filter(scanned_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(scanned_at__date__lte=date_to)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    classes = Class.objects.filter(is_active=True)
    
    return render(request, 'attendance/qr_logs.html', {
        'page_obj': page_obj,
        'classes': classes,
        'selected_class': class_id,
        'selected_result': result,
    })
