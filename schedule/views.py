"""
일정/캘린더 뷰
"""
from datetime import datetime, timedelta
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import CalendarEvent, MakeupClass, HolidayRange
from .forms import CalendarEventForm, MakeupClassForm, HolidayRangeForm
from classes.models import Class
from teachers.models import Teacher


# 색상 팔레트
COLORS = {
    'class': '#4285f4',
    'makeup': '#34a853',
    'holiday': '#ea4335',
    'special': '#fbbc04',
    'camp': '#9c27b0',
    'other': '#607d8b',
}


@login_required
def calendar_view(request):
    """캘린더 페이지"""
    classes = Class.objects.filter(is_active=True)
    teachers = Teacher.objects.select_related('employee__user').filter(is_active=True)
    
    return render(request, 'schedule/calendar.html', {
        'classes': classes,
        'teachers': teachers,
    })


@login_required
def calendar_api(request):
    """FullCalendar용 이벤트 API"""
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
    
    events = []
    
    # 1. CalendarEvent 조회
    calendar_events = CalendarEvent.objects.filter(
        start_date__lte=end_date,
    ).filter(
        models.Q(end_date__gte=start_date) | models.Q(end_date__isnull=True, start_date__gte=start_date)
    )
    
    if class_id:
        calendar_events = calendar_events.filter(assigned_class_id=class_id)
    if teacher_id:
        calendar_events = calendar_events.filter(teacher_id=teacher_id)
    
    for event in calendar_events:
        event_data = {
            'id': f'event_{event.id}',
            'title': event.title,
            'backgroundColor': event.color or COLORS.get(event.event_type, '#607d8b'),
            'borderColor': event.color or COLORS.get(event.event_type, '#607d8b'),
            'allDay': event.all_day,
            'extendedProps': {
                'type': event.event_type,
                'type_display': event.get_event_type_display(),
                'description': event.description,
                'class_name': event.assigned_class.name if event.assigned_class else '',
                'teacher': event.teacher.name if event.teacher else '',
                'location': event.location,
            }
        }
        
        if event.all_day:
            event_data['start'] = event.start_date.isoformat()
            if event.end_date:
                event_data['end'] = (event.end_date + timedelta(days=1)).isoformat()
        else:
            if event.start_time:
                event_data['start'] = f"{event.start_date.isoformat()}T{event.start_time.isoformat()}"
            else:
                event_data['start'] = event.start_date.isoformat()
            if event.end_date and event.end_time:
                event_data['end'] = f"{event.end_date.isoformat()}T{event.end_time.isoformat()}"
            elif event.end_time:
                event_data['end'] = f"{event.start_date.isoformat()}T{event.end_time.isoformat()}"
        
        events.append(event_data)
    
    # 2. HolidayRange 조회
    holidays = HolidayRange.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    for holiday in holidays:
        events.append({
            'id': f'holiday_{holiday.id}',
            'title': f'🔴 {holiday.title}',
            'start': holiday.start_date.isoformat(),
            'end': (holiday.end_date + timedelta(days=1)).isoformat(),
            'backgroundColor': '#ea4335',
            'borderColor': '#ea4335',
            'allDay': True,
            'display': 'background',
            'extendedProps': {
                'type': 'holiday',
                'type_display': holiday.get_holiday_type_display(),
                'description': holiday.description,
            }
        })
    
    # 3. 정규 수업 (Class 기반)
    from timetable.views import WEEKDAY_MAP
    
    classes_qs = Class.objects.filter(is_active=True).select_related('teacher__employee__user')
    if class_id:
        classes_qs = classes_qs.filter(id=class_id)
    if teacher_id:
        classes_qs = classes_qs.filter(teacher_id=teacher_id)
    
    color_index = 0
    class_colors = ['#4285f4', '#34a853', '#9c27b0', '#ff5722', '#00bcd4', '#795548']
    
    for cls in classes_qs:
        if not cls.weekdays or not cls.start_time or not cls.end_time:
            continue
        
        weekdays = [w.strip() for w in cls.weekdays.split(',')]
        color = class_colors[color_index % len(class_colors)]
        color_index += 1
        
        current_date = start_date
        while current_date <= end_date:
            current_weekday = current_date.weekday()
            
            for day in weekdays:
                if WEEKDAY_MAP.get(day.lower()) == current_weekday:
                    events.append({
                        'id': f"class_{cls.id}_{current_date.isoformat()}",
                        'title': cls.name,
                        'start': f"{current_date.isoformat()}T{cls.start_time.isoformat()}",
                        'end': f"{current_date.isoformat()}T{cls.end_time.isoformat()}",
                        'backgroundColor': color,
                        'borderColor': color,
                        'extendedProps': {
                            'type': 'regular_class',
                            'type_display': '정규 수업',
                            'class_id': cls.id,
                            'teacher': cls.teacher.name if cls.teacher else '',
                            'subject': cls.subject,
                            'student_count': cls.student_count,
                            'max_students': cls.max_students,
                        }
                    })
                    break
            
            current_date += timedelta(days=1)
    
    return JsonResponse(events, safe=False)


@login_required
def event_create(request):
    """이벤트 생성"""
    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, '일정이 등록되었습니다.')
            return redirect('schedule:calendar')
    else:
        # 날짜 파라미터가 있으면 기본값 설정
        initial = {}
        date_str = request.GET.get('date')
        if date_str:
            try:
                initial['start_date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        form = CalendarEventForm(initial=initial)
    
    return render(request, 'schedule/event_form.html', {
        'form': form,
        'title': '일정 등록',
    })


@login_required
def event_update(request, pk):
    """이벤트 수정"""
    event = get_object_or_404(CalendarEvent, pk=pk)
    
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, '일정이 수정되었습니다.')
            return redirect('schedule:calendar')
    else:
        form = CalendarEventForm(instance=event)
    
    return render(request, 'schedule/event_form.html', {
        'form': form,
        'event': event,
        'title': '일정 수정',
    })


@login_required
def event_delete(request, pk):
    """이벤트 삭제"""
    event = get_object_or_404(CalendarEvent, pk=pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, '일정이 삭제되었습니다.')
        return redirect('schedule:calendar')
    
    return render(request, 'schedule/event_confirm_delete.html', {
        'event': event,
    })


@login_required
def holiday_list(request):
    """휴원 기간 목록"""
    holidays = HolidayRange.objects.all()
    return render(request, 'schedule/holiday_list.html', {
        'holidays': holidays,
    })


@login_required
def holiday_create(request):
    """휴원 기간 등록"""
    if request.method == 'POST':
        form = HolidayRangeForm(request.POST)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.created_by = request.user
            holiday.save()
            form.save_m2m()  # ManyToMany 저장
            messages.success(request, '휴원 기간이 등록되었습니다.')
            return redirect('schedule:holiday_list')
    else:
        form = HolidayRangeForm()
    
    return render(request, 'schedule/holiday_form.html', {
        'form': form,
        'title': '휴원 기간 등록',
    })


@login_required
def holiday_update(request, pk):
    """휴원 기간 수정"""
    holiday = get_object_or_404(HolidayRange, pk=pk)
    
    if request.method == 'POST':
        form = HolidayRangeForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, '휴원 기간이 수정되었습니다.')
            return redirect('schedule:holiday_list')
    else:
        form = HolidayRangeForm(instance=holiday)
    
    return render(request, 'schedule/holiday_form.html', {
        'form': form,
        'holiday': holiday,
        'title': '휴원 기간 수정',
    })


@login_required
def holiday_delete(request, pk):
    """휴원 기간 삭제"""
    holiday = get_object_or_404(HolidayRange, pk=pk)
    
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, '휴원 기간이 삭제되었습니다.')
        return redirect('schedule:holiday_list')
    
    return render(request, 'schedule/holiday_confirm_delete.html', {
        'holiday': holiday,
    })


@login_required
def makeup_list(request):
    """보강 수업 목록"""
    makeups = MakeupClass.objects.select_related(
        'original_class', 'makeup_event'
    ).all()
    return render(request, 'schedule/makeup_list.html', {
        'makeups': makeups,
    })


@login_required 
def makeup_create(request):
    """보강 수업 등록"""
    if request.method == 'POST':
        form = MakeupClassForm(request.POST)
        event_form = CalendarEventForm(request.POST, prefix='event')
        
        if form.is_valid() and event_form.is_valid():
            # 먼저 이벤트 생성
            event = event_form.save(commit=False)
            event.event_type = 'makeup'
            event.created_by = request.user
            event.save()
            
            # 보강 수업 생성
            makeup = form.save(commit=False)
            makeup.makeup_event = event
            makeup.created_by = request.user
            makeup.save()
            
            messages.success(request, '보강 수업이 등록되었습니다.')
            return redirect('schedule:makeup_list')
    else:
        form = MakeupClassForm()
        event_form = CalendarEventForm(prefix='event')
    
    return render(request, 'schedule/makeup_form.html', {
        'form': form,
        'event_form': event_form,
        'title': '보강 수업 등록',
    })


# views.py에 추가 import
from django.db import models
