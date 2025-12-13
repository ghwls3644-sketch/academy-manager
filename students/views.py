from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Student
from .forms import StudentForm, StudentSearchForm


@login_required
def student_list(request):
    """학생 목록"""
    students = Student.objects.select_related('assigned_class').all()
    form = StudentSearchForm(request.GET)
    
    # 검색
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(parent_phone__icontains=search)
        )
    
    # 상태 필터
    status = request.GET.get('status', '')
    if status:
        students = students.filter(status=status)
    
    # 반 필터
    assigned_class = request.GET.get('assigned_class', '')
    if assigned_class:
        students = students.filter(assigned_class_id=assigned_class)
    
    # 통계
    stats = {
        'total': Student.objects.count(),
        'enrolled': Student.objects.filter(status='enrolled').count(),
        'paused': Student.objects.filter(status='paused').count(),
        'withdrawn': Student.objects.filter(status='withdrawn').count(),
    }
    
    # 페이지네이션
    paginator = Paginator(students, 15)
    page = request.GET.get('page', 1)
    students = paginator.get_page(page)
    
    return render(request, 'students/student_list.html', {
        'students': students,
        'form': form,
        'search': search,
        'status': status,
        'assigned_class': assigned_class,
        'stats': stats,
    })


@login_required
def student_create(request):
    """학생 등록"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '학생이 등록되었습니다.')
            return redirect('students:list')
    else:
        initial = {}
        # URL에서 반 정보 받기
        class_id = request.GET.get('class')
        if class_id:
            initial['assigned_class'] = class_id
        form = StudentForm(initial=initial)
    
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': '학생 등록',
    })


@login_required
def student_detail(request, pk):
    """학생 상세"""
    student = get_object_or_404(Student.objects.select_related('assigned_class'), pk=pk)
    
    # 출결 및 수납 내역 (나중에 구현될 앱과 연동)
    attendances = []
    payments = []
    if hasattr(student, 'attendances'):
        attendances = student.attendances.order_by('-date')[:10]
    if hasattr(student, 'payments'):
        payments = student.payments.order_by('-payment_date')[:5]
    
    return render(request, 'students/student_detail.html', {
        'student': student,
        'attendances': attendances,
        'payments': payments,
    })


@login_required
def student_update(request, pk):
    """학생 수정"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '학생 정보가 수정되었습니다.')
            return redirect('students:detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/student_form.html', {
        'form': form,
        'student': student,
        'title': '학생 수정',
    })


@login_required
def student_delete(request, pk):
    """학생 삭제"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, '학생이 삭제되었습니다.')
        return redirect('students:list')
    
    return render(request, 'students/student_confirm_delete.html', {
        'student': student,
    })
