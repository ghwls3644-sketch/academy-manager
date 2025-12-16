"""
시간표/캘린더 뷰
"""
from datetime import datetime, timedelta
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from classes.models import Class
from teachers.models import Teacher


# 요일 매핑 (월=0, 일=6)
WEEKDAY_MAP = {
    'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 
    'fri': 4, 'sat': 5, 'sun': 6
}

# 색상 팔레트
COLORS = [
    '#4285f4', '#ea4335', '#34a853', '#fbbc04', 
    '#9c27b0', '#ff5722', '#00bcd4', '#795548',
    '#607d8b', '#e91e63'
]


@login_required
def timetable_view(request):
    """시간표 캘린더 페이지"""
    classes = Class.objects.filter(is_active=True)
    teachers = Teacher.objects.select_related('employee__user').filter(is_active=True)
    
    return render(request, 'timetable/index.html', {
        'classes': classes,
        'teachers': teachers,
    })


@login_required
def timetable_api(request):
    """FullCalendar용 이벤트 API"""
    # 파라미터
    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    class_id = request.GET.get('class_id')
    teacher_id = request.GET.get('teacher_id')
    
    # 날짜 파싱
    try:
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
    except (ValueError, AttributeError):
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date() + timedelta(days=60)
    
    # 반 목록 조회
    classes = Class.objects.filter(is_active=True).select_related('teacher__employee__user')
    
    if class_id:
        classes = classes.filter(id=class_id)
    if teacher_id:
        classes = classes.filter(teacher_id=teacher_id)
    
    events = []
    color_index = 0
    
    for cls in classes:
        if not cls.weekdays or not cls.start_time or not cls.end_time:
            continue
        
        weekdays = [w.strip() for w in cls.weekdays.split(',')]
        color = COLORS[color_index % len(COLORS)]
        color_index += 1
        
        # 날짜 범위 내의 모든 해당 요일에 이벤트 생성
        current_date = start_date
        while current_date <= end_date:
            current_weekday = current_date.weekday()
            
            for day in weekdays:
                if WEEKDAY_MAP.get(day.lower()) == current_weekday:
                    events.append({
                        'id': f"{cls.id}_{current_date.isoformat()}",
                        'title': cls.name,
                        'start': f"{current_date.isoformat()}T{cls.start_time.isoformat()}",
                        'end': f"{current_date.isoformat()}T{cls.end_time.isoformat()}",
                        'backgroundColor': color,
                        'borderColor': color,
                        'extendedProps': {
                            'class_id': cls.id,
                            'teacher': cls.teacher.employee.user.get_full_name() if cls.teacher else '',
                            'subject': cls.subject,
                            'student_count': cls.student_count,
                            'max_students': cls.max_students,
                        }
                    })
                    break
            
            current_date += timedelta(days=1)
    
    return JsonResponse(events, safe=False)
