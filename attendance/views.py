from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm
from students.models import Student
from classes.models import Class
from core.utils import parse_date_safe

logger = logging.getLogger(__name__)


@login_required
def attendance_list(request):
    """출결 목록"""
    attendances = Attendance.objects.select_related('student', 'assigned_class').all()
    
    # 날짜 필터 - 유틸 함수 사용
    date_str = request.GET.get('date', '')
    if date_str:
        filter_date = parse_date_safe(date_str, default=None)
        if filter_date:
            attendances = attendances.filter(date=filter_date)
    
    # 반 필터
    class_id = request.GET.get('class', '')
    if class_id:
        attendances = attendances.filter(assigned_class_id=class_id)
    
    # 학생 필터
    student_id = request.GET.get('student', '')
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    
    # 상태 필터
    status = request.GET.get('status', '')
    if status:
        attendances = attendances.filter(status=status)
    
    # 정렬 및 페이지네이션
    attendances = attendances.order_by('-date', '-id')
    paginator = Paginator(attendances, 20)
    page = request.GET.get('page', 1)
    attendances = paginator.get_page(page)
    
    # 활성 반 목록
    classes = Class.objects.filter(is_active=True)
    
    return render(request, 'attendance/attendance_list.html', {
        'attendances': attendances,
        'classes': classes,
        'date': date_str,
        'class_id': class_id,
        'student_id': student_id,
        'status': status,
    })


@login_required
def attendance_create(request):
    """출결 등록"""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '출결이 등록되었습니다.')
            return redirect('attendance:list')
    else:
        initial = {'date': timezone.now().date()}
        form = AttendanceForm(initial=initial)
    
    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': '출결 등록',
    })


@login_required
def attendance_update(request, pk):
    """출결 수정"""
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, '출결이 수정되었습니다.')
            return redirect('attendance:list')
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'attendance': attendance,
        'title': '출결 수정',
    })


@login_required
def attendance_delete(request, pk):
    """출결 삭제"""
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, '출결 기록이 삭제되었습니다.')
        return redirect('attendance:list')
    
    return render(request, 'attendance/attendance_confirm_delete.html', {
        'attendance': attendance,
    })


@login_required
def attendance_bulk(request):
    """일괄 출결 입력"""
    if request.method == 'POST':
        class_id = request.POST.get('assigned_class')
        date_str = request.POST.get('date')
        
        if not class_id:
            messages.error(request, '반을 선택해주세요.')
            return redirect('attendance:bulk')
        
        if not date_str:
            messages.error(request, '날짜를 입력해주세요.')
            return redirect('attendance:bulk')
        
        try:
            # 날짜 파싱
            filter_date = parse_date_safe(date_str, default=None)
            if not filter_date:
                messages.error(request, '날짜 형식이 올바르지 않습니다. (예: 2024-12-25)')
                return redirect('attendance:bulk')
            
            # 반 조회
            try:
                class_obj = Class.objects.get(pk=class_id)
            except Class.DoesNotExist:
                messages.error(request, '선택한 반을 찾을 수 없습니다.')
                return redirect('attendance:bulk')
            
            # 학생 목록 조회
            students = Student.objects.filter(assigned_class=class_obj, status='enrolled')
            
            if not students.exists():
                messages.warning(request, '해당 반에 등록된 학생이 없습니다.')
                return redirect('attendance:bulk')
            
            # 출결 처리
            processed_count = 0
            for student in students:
                status = request.POST.get(f'status_{student.pk}', 'present')
                note = request.POST.get(f'note_{student.pk}', '')
                
                Attendance.objects.update_or_create(
                    student=student,
                    date=filter_date,
                    defaults={
                        'assigned_class': class_obj,
                        'status': status,
                        'note': note
                    }
                )
                processed_count += 1
            
            messages.success(request, f'{processed_count}명의 출결이 처리되었습니다.')
            return redirect('attendance:list')
            
        except Exception as e:
            logger.exception("일괄 출결 처리 중 오류 발생")
            messages.error(request, '처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    
    # GET 요청 또는 POST 이후 form 표시
    form = BulkAttendanceForm(request.GET or None)
    class_id = request.GET.get('assigned_class', '')
    date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    
    students = []
    existing_attendances = {}
    
    if class_id:
        students = Student.objects.filter(
            assigned_class_id=class_id, 
            status='enrolled'
        ).order_by('name')
        
        filter_date = parse_date_safe(date_str, default=None)
        if filter_date:
            for att in Attendance.objects.filter(
                assigned_class_id=class_id, 
                date=filter_date
            ).select_related('student'):
                existing_attendances[att.student_id] = att
    
    return render(request, 'attendance/attendance_bulk.html', {
        'form': form,
        'students': students,
        'existing_attendances': existing_attendances,
        'class_id': class_id,
        'date': date_str,
        'status_choices': Attendance.STATUS_CHOICES,
    })

