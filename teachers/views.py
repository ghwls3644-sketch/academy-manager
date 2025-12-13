from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Teacher
from .forms import TeacherForm


@login_required
def teacher_list(request):
    """강사 목록"""
    teachers = Teacher.objects.select_related('employee__user').all()
    
    # 검색
    search = request.GET.get('search', '')
    if search:
        teachers = teachers.filter(
            employee__user__first_name__icontains=search
        ) | teachers.filter(
            employee__user__username__icontains=search
        ) | teachers.filter(
            subject__icontains=search
        )
    
    # 페이지네이션
    paginator = Paginator(teachers, 10)
    page = request.GET.get('page', 1)
    teachers = paginator.get_page(page)
    
    return render(request, 'teachers/teacher_list.html', {
        'teachers': teachers,
        'search': search,
    })


@login_required
def teacher_create(request):
    """강사 등록"""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '강사가 등록되었습니다.')
            return redirect('teachers:list')
    else:
        form = TeacherForm()
    
    return render(request, 'teachers/teacher_form.html', {
        'form': form,
        'title': '강사 등록',
    })


@login_required
def teacher_detail(request, pk):
    """강사 상세"""
    teacher = get_object_or_404(Teacher.objects.select_related('employee__user'), pk=pk)
    
    # 담당 반 목록
    classes = teacher.classes.all() if hasattr(teacher, 'classes') else []
    
    return render(request, 'teachers/teacher_detail.html', {
        'teacher': teacher,
        'classes': classes,
    })


@login_required
def teacher_update(request, pk):
    """강사 수정"""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, '강사 정보가 수정되었습니다.')
            return redirect('teachers:detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)
    
    return render(request, 'teachers/teacher_form.html', {
        'form': form,
        'teacher': teacher,
        'title': '강사 수정',
    })


@login_required
def teacher_delete(request, pk):
    """강사 삭제"""
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        # 관련 User, Employee도 함께 삭제
        user = teacher.employee.user
        teacher.delete()
        teacher.employee.delete()
        user.delete()
        messages.success(request, '강사가 삭제되었습니다.')
        return redirect('teachers:list')
    
    return render(request, 'teachers/teacher_confirm_delete.html', {
        'teacher': teacher,
    })
