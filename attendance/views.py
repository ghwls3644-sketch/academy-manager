from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm
from students.models import Student
from classes.models import Class


@login_required
def attendance_list(request):
    """출결 목록"""
    attendances = Attendance.objects.select_related('student', 'assigned_class').all()
    
    # 날짜 필터
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            attendances = attendances.filter(date=filter_date)
        except:
            pass
    
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
    
    # 페이지네이션
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
        
        if class_id and date_str:
            try:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                class_obj = Class.objects.get(pk=class_id)
                students = Student.objects.filter(assigned_class=class_obj, status='enrolled')
                
                created_count = 0
                for student in students:
                    status = request.POST.get(f'status_{student.pk}', 'present')
                    note = request.POST.get(f'note_{student.pk}', '')
                    
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        date=filter_date,
                        defaults={
                            'assigned_class': class_obj,
                            'status': status,
                            'note': note
                        }
                    )
                    if created:
                        created_count += 1
                
                messages.success(request, f'{len(students)}명의 출결이 처리되었습니다.')
                return redirect('attendance:list')
            except Exception as e:
                messages.error(request, f'오류가 발생했습니다: {str(e)}')
    
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
        
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                for att in Attendance.objects.filter(
                    assigned_class_id=class_id, 
                    date=filter_date
                ):
                    existing_attendances[att.student_id] = att
            except:
                pass
    
    return render(request, 'attendance/attendance_bulk.html', {
        'form': form,
        'students': students,
        'existing_attendances': existing_attendances,
        'class_id': class_id,
        'date': date_str,
        'status_choices': Attendance.STATUS_CHOICES,
    })
