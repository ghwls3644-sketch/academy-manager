from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Class
from .forms import ClassForm


@login_required
def class_list(request):
    """반 목록"""
    classes = Class.objects.select_related('teacher__employee__user').all()
    
    # 검색
    search = request.GET.get('search', '')
    if search:
        classes = classes.filter(name__icontains=search) | classes.filter(subject__icontains=search)
    
    # 필터
    status = request.GET.get('status', '')
    if status == 'active':
        classes = classes.filter(is_active=True)
    elif status == 'inactive':
        classes = classes.filter(is_active=False)
    
    # 페이지네이션
    paginator = Paginator(classes, 10)
    page = request.GET.get('page', 1)
    classes = paginator.get_page(page)
    
    return render(request, 'classes/class_list.html', {
        'classes': classes,
        'search': search,
        'status': status,
    })


@login_required
def class_create(request):
    """반 등록"""
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '반이 등록되었습니다.')
            return redirect('classes:list')
    else:
        form = ClassForm()
    
    return render(request, 'classes/class_form.html', {
        'form': form,
        'title': '반 등록',
    })


@login_required
def class_detail(request, pk):
    """반 상세"""
    class_obj = get_object_or_404(Class.objects.select_related('teacher__employee__user'), pk=pk)
    students = class_obj.students.all() if hasattr(class_obj, 'students') else []
    
    return render(request, 'classes/class_detail.html', {
        'class': class_obj,
        'students': students,
    })


@login_required
def class_update(request, pk):
    """반 수정"""
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '반 정보가 수정되었습니다.')
            return redirect('classes:detail', pk=pk)
    else:
        form = ClassForm(instance=class_obj)
    
    return render(request, 'classes/class_form.html', {
        'form': form,
        'class': class_obj,
        'title': '반 수정',
    })


@login_required
def class_delete(request, pk):
    """반 삭제"""
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, '반이 삭제되었습니다.')
        return redirect('classes:list')
    
    return render(request, 'classes/class_confirm_delete.html', {
        'class': class_obj,
    })
