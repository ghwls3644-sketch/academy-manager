from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from students.models import Student
from classes.models import Class
from teachers.models import Teacher


@login_required
def global_search(request):
    """전역 검색 API - 학생/반/강사 통합 검색"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'students': [],
            'classes': [],
            'teachers': [],
            'total': 0
        })
    
    # 학생 검색 (이름, 전화번호, 학부모 전화번호)
    students = Student.objects.filter(
        Q(name__icontains=query) |
        Q(phone__icontains=query) |
        Q(parent_phone__icontains=query)
    ).select_related('assigned_class')[:5]
    
    students_data = [{
        'id': s.id,
        'name': s.name,
        'phone': s.phone or '-',
        'status': s.get_status_display(),
        'status_class': f'status-{s.status}',
        'class_name': s.assigned_class.name if s.assigned_class else '-',
        'url': f'/students/{s.id}/'
    } for s in students]
    
    # 반 검색 (반 이름, 과목)
    classes = Class.objects.filter(
        Q(name__icontains=query) |
        Q(subject__icontains=query)
    ).select_related('teacher__employee')[:5]
    
    classes_data = [{
        'id': c.id,
        'name': c.name,
        'subject': c.subject or '-',
        'teacher': str(c.teacher) if c.teacher else '-',
        'student_count': c.student_count,
        'url': f'/classes/{c.id}/'
    } for c in classes]
    
    # 강사 검색 (사용자 이름, 과목)
    teachers = Teacher.objects.filter(
        Q(employee__user__username__icontains=query) |
        Q(employee__user__first_name__icontains=query) |
        Q(employee__user__last_name__icontains=query) |
        Q(subject__icontains=query)
    ).select_related('employee__user')[:5]
    
    teachers_data = [{
        'id': t.id,
        'name': str(t),
        'subject': t.subject or '-',
        'phone': t.phone or '-',
        'url': f'/teachers/{t.id}/'
    } for t in teachers]
    
    total = len(students_data) + len(classes_data) + len(teachers_data)
    
    return JsonResponse({
        'students': students_data,
        'classes': classes_data,
        'teachers': teachers_data,
        'total': total,
        'query': query
    })
