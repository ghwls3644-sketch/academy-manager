"""
알림 시스템 뷰
"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import NotificationTemplate, NotificationJob, NotificationLog
from .forms import NotificationTemplateForm, NotificationSendForm
from students.models import Student


def replace_variables(content, context):
    """변수 치환"""
    for key, value in context.items():
        content = content.replace('{' + key + '}', str(value))
    return content


@login_required
def template_list(request):
    """템플릿 목록"""
    templates = NotificationTemplate.objects.all()
    
    # 필터
    channel = request.GET.get('channel')
    trigger = request.GET.get('trigger')
    
    if channel:
        templates = templates.filter(channel=channel)
    if trigger:
        templates = templates.filter(trigger_type=trigger)
    
    return render(request, 'notifications/template_list.html', {
        'templates': templates,
        'channel_choices': NotificationTemplate.CHANNEL_CHOICES,
        'trigger_choices': NotificationTemplate.TRIGGER_CHOICES,
    })


@login_required
def template_create(request):
    """템플릿 생성"""
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, '알림 템플릿이 생성되었습니다.')
            return redirect('notifications:template_list')
    else:
        form = NotificationTemplateForm()
    
    return render(request, 'notifications/template_form.html', {
        'form': form,
        'title': '템플릿 생성',
    })


@login_required
def template_update(request, pk):
    """템플릿 수정"""
    template = get_object_or_404(NotificationTemplate, pk=pk)
    
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, '알림 템플릿이 수정되었습니다.')
            return redirect('notifications:template_list')
    else:
        form = NotificationTemplateForm(instance=template)
    
    return render(request, 'notifications/template_form.html', {
        'form': form,
        'template': template,
        'title': '템플릿 수정',
    })


@login_required
def template_delete(request, pk):
    """템플릿 삭제"""
    template = get_object_or_404(NotificationTemplate, pk=pk)
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, '알림 템플릿이 삭제되었습니다.')
        return redirect('notifications:template_list')
    
    return render(request, 'notifications/template_confirm_delete.html', {
        'template': template,
    })


@login_required
def send_notification(request):
    """알림 발송"""
    if request.method == 'POST':
        form = NotificationSendForm(request.POST)
        if form.is_valid():
            # 대상 학생 결정
            target_type = form.cleaned_data['target_type']
            students = []
            
            if target_type == 'student':
                students = list(form.cleaned_data['target_students'])
            elif target_type == 'class':
                target_class = form.cleaned_data['target_class']
                if target_class:
                    students = list(target_class.students.filter(status='enrolled'))
            elif target_type == 'all':
                students = list(Student.objects.filter(status='enrolled'))
            
            if not students:
                messages.error(request, '발송 대상이 없습니다.')
            else:
                # 발송 작업 생성
                job = NotificationJob.objects.create(
                    template=form.cleaned_data['template'],
                    target_type=target_type,
                    target_class=form.cleaned_data.get('target_class'),
                    subject=form.cleaned_data.get('subject', ''),
                    content=form.cleaned_data['content'],
                    scheduled_at=form.cleaned_data.get('scheduled_at'),
                    total_count=len(students),
                    created_by=request.user,
                )
                job.target_students.set(students)
                
                # 예약 발송이 아니면 즉시 처리 (시뮬레이션)
                if not job.scheduled_at:
                    success_count = 0
                    for student in students:
                        # 변수 치환
                        context = {
                            '학생명': student.name,
                            '반명': student.assigned_class.name if student.assigned_class else '',
                        }
                        sent_content = replace_variables(job.content, context)
                        
                        # 로그 생성 (실제로는 SMS API 호출)
                        recipient_contact = student.parent_phone or student.phone or '-'
                        
                        NotificationLog.objects.create(
                            job=job,
                            recipient_name=student.name,
                            recipient_contact=recipient_contact,
                            sent_content=sent_content,
                            result='success',  # 시뮬레이션
                        )
                        success_count += 1
                    
                    job.status = 'sent'
                    job.success_count = success_count
                    job.processed_at = timezone.now()
                    job.save()
                    
                    messages.success(request, f'{success_count}건의 알림이 발송되었습니다.')
                else:
                    messages.success(request, f'{len(students)}건의 알림이 예약되었습니다.')
                
                return redirect('notifications:job_list')
    else:
        initial = {}
        template_id = request.GET.get('template')
        if template_id:
            try:
                template = NotificationTemplate.objects.get(pk=template_id)
                initial['template'] = template
                initial['subject'] = template.subject
                initial['content'] = template.content
            except NotificationTemplate.DoesNotExist:
                pass
        
        form = NotificationSendForm(initial=initial)
    
    return render(request, 'notifications/send.html', {
        'form': form,
    })


@login_required
def job_list(request):
    """발송 작업 목록"""
    jobs = NotificationJob.objects.select_related('template', 'created_by').all()
    
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)
    
    return render(request, 'notifications/job_list.html', {
        'jobs': jobs,
        'status_choices': NotificationJob.STATUS_CHOICES,
    })


@login_required
def job_detail(request, pk):
    """발송 작업 상세"""
    job = get_object_or_404(NotificationJob, pk=pk)
    logs = job.logs.all()[:100]  # 최근 100건
    
    return render(request, 'notifications/job_detail.html', {
        'job': job,
        'logs': logs,
    })


@login_required
def template_preview(request):
    """템플릿 미리보기 API"""
    template_id = request.GET.get('template_id')
    if template_id:
        try:
            template = NotificationTemplate.objects.get(pk=template_id)
            return JsonResponse({
                'subject': template.subject,
                'content': template.content,
            })
        except NotificationTemplate.DoesNotExist:
            pass
    
    return JsonResponse({'subject': '', 'content': ''})


# === 주간/월간 보고서 ===

from .models import WeeklyReport
from datetime import timedelta


@login_required
def report_list(request):
    """보고서 목록"""
    reports = WeeklyReport.objects.select_related('student', 'created_by').all()
    
    period = request.GET.get('period')
    status = request.GET.get('status')
    
    if period:
        reports = reports.filter(period_type=period)
    if status:
        reports = reports.filter(status=status)
    
    return render(request, 'notifications/report_list.html', {
        'reports': reports,
        'period_choices': WeeklyReport.PERIOD_CHOICES,
        'status_choices': WeeklyReport.STATUS_CHOICES,
    })


@login_required
def report_create(request):
    """보고서 생성"""
    if request.method == 'POST':
        student_id = request.POST.get('student')
        period_type = request.POST.get('period_type', 'weekly')
        
        from students.models import Student
        student = get_object_or_404(Student, pk=student_id)
        
        today = timezone.now().date()
        if period_type == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            title = f"{start_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')} 주간 보고서"
        else:
            from calendar import monthrange
            start_date = today.replace(day=1)
            end_date = today.replace(day=monthrange(today.year, today.month)[1])
            title = f"{today.month}월 월간 보고서"
        
        report = WeeklyReport.objects.create(
            student=student,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            title=title,
            created_by=request.user,
        )
        
        # 통계 자동 계산
        report.calculate_stats()
        report.save()
        
        messages.success(request, '보고서가 생성되었습니다.')
        return redirect('notifications:report_edit', pk=report.pk)
    
    from students.models import Student
    students = Student.objects.filter(status='enrolled')
    
    return render(request, 'notifications/report_create.html', {
        'students': students,
        'period_choices': WeeklyReport.PERIOD_CHOICES,
    })


@login_required
def report_edit(request, pk):
    """보고서 수정"""
    report = get_object_or_404(WeeklyReport, pk=pk)
    
    if request.method == 'POST':
        report.learning_summary = request.POST.get('learning_summary', '')
        report.teacher_comment = request.POST.get('teacher_comment', '')
        report.homework_status = request.POST.get('homework_status', '')
        report.next_plan = request.POST.get('next_plan', '')
        report.save()
        
        action = request.POST.get('action')
        if action == 'ready':
            report.status = 'ready'
            report.save()
            messages.success(request, '보고서가 발송 대기 상태로 변경되었습니다.')
        else:
            messages.success(request, '보고서가 저장되었습니다.')
        
        return redirect('notifications:report_list')
    
    return render(request, 'notifications/report_edit.html', {
        'report': report,
    })


@login_required
def report_detail(request, pk):
    """보고서 상세"""
    report = get_object_or_404(WeeklyReport, pk=pk)
    
    return render(request, 'notifications/report_detail.html', {
        'report': report,
    })

