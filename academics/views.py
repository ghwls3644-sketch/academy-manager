"""
성적/학습 관리 뷰
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Q
from decimal import Decimal

from .models import Subject, Exam, Score, LearningGoal, ReportCard
from .forms import SubjectForm, ExamForm, ScoreForm, ScoreBulkForm, LearningGoalForm, ReportCardForm
from students.models import Student
from classes.models import Class


@login_required
def exam_list(request):
    """시험 목록"""
    exams = Exam.objects.select_related('subject', 'assigned_class').all()
    
    # 필터
    subject_id = request.GET.get('subject')
    class_id = request.GET.get('class')
    
    if subject_id:
        exams = exams.filter(subject_id=subject_id)
    if class_id:
        exams = exams.filter(assigned_class_id=class_id)
    
    subjects = Subject.objects.filter(is_active=True)
    classes = Class.objects.filter(is_active=True)
    
    return render(request, 'academics/exam_list.html', {
        'exams': exams,
        'subjects': subjects,
        'classes': classes,
    })


@login_required
def exam_create(request):
    """시험 등록"""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, '시험이 등록되었습니다.')
            return redirect('academics:exam_list')
    else:
        form = ExamForm()
    
    return render(request, 'academics/exam_form.html', {
        'form': form,
        'title': '시험 등록',
    })


@login_required
def exam_update(request, pk):
    """시험 수정"""
    exam = get_object_or_404(Exam, pk=pk)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, '시험이 수정되었습니다.')
            return redirect('academics:exam_list')
    else:
        form = ExamForm(instance=exam)
    
    return render(request, 'academics/exam_form.html', {
        'form': form,
        'exam': exam,
        'title': '시험 수정',
    })


@login_required
def exam_detail(request, pk):
    """시험 상세 및 성적 입력"""
    exam = get_object_or_404(Exam, pk=pk)
    scores = exam.scores.select_related('student').order_by('-score')
    
    # 대상 학생 (해당 반 또는 전체)
    if exam.assigned_class:
        available_students = exam.assigned_class.students.filter(status='enrolled')
    else:
        available_students = Student.objects.filter(status='enrolled')
    
    # 이미 점수가 입력된 학생 ID
    scored_student_ids = set(scores.values_list('student_id', flat=True))
    unscored_students = available_students.exclude(id__in=scored_student_ids)
    
    # 통계
    stats = {
        'count': scores.count(),
        'average': round(scores.aggregate(avg=Avg('score'))['avg'] or 0, 1),
        'max_score': max(s.score for s in scores) if scores else 0,
        'min_score': min(s.score for s in scores) if scores else 0,
    }
    
    return render(request, 'academics/exam_detail.html', {
        'exam': exam,
        'scores': scores,
        'unscored_students': unscored_students,
        'stats': stats,
    })


@login_required
def score_create(request, exam_pk):
    """성적 입력"""
    exam = get_object_or_404(Exam, pk=exam_pk)
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        score_value = request.POST.get('score')
        feedback = request.POST.get('feedback', '')
        
        if student_id and score_value:
            student = get_object_or_404(Student, pk=student_id)
            
            # 이미 입력된 성적 확인
            score, created = Score.objects.update_or_create(
                exam=exam,
                student=student,
                defaults={
                    'score': Decimal(score_value),
                    'feedback': feedback,
                }
            )
            
            if created:
                messages.success(request, f'{student.name} 학생의 성적이 입력되었습니다.')
            else:
                messages.success(request, f'{student.name} 학생의 성적이 수정되었습니다.')
        
        return redirect('academics:exam_detail', pk=exam.pk)
    
    return redirect('academics:exam_detail', pk=exam.pk)


@login_required
def score_bulk_create(request, exam_pk):
    """성적 일괄 입력"""
    exam = get_object_or_404(Exam, pk=exam_pk)
    
    if exam.assigned_class:
        students = exam.assigned_class.students.filter(status='enrolled')
    else:
        students = Student.objects.filter(status='enrolled')
    
    if request.method == 'POST':
        count = 0
        for student in students:
            score_value = request.POST.get(f'score_{student.id}')
            if score_value:
                Score.objects.update_or_create(
                    exam=exam,
                    student=student,
                    defaults={'score': Decimal(score_value)}
                )
                count += 1
        
        messages.success(request, f'{count}명의 성적이 입력되었습니다.')
        return redirect('academics:exam_detail', pk=exam.pk)
    
    # 기존 성적 가져오기
    existing_scores = {s.student_id: s.score for s in exam.scores.all()}
    
    return render(request, 'academics/score_bulk_form.html', {
        'exam': exam,
        'students': students,
        'existing_scores': existing_scores,
    })


@login_required
def student_scores(request, student_pk):
    """학생별 성적 조회"""
    student = get_object_or_404(Student, pk=student_pk)
    scores = student.scores.select_related('exam', 'exam__subject').order_by('-exam__exam_date')
    
    # 과목별 평균
    subject_stats = {}
    for score in scores:
        subject_name = score.exam.subject.name if score.exam.subject else '기타'
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {'scores': [], 'total': 0, 'count': 0}
        subject_stats[subject_name]['scores'].append(float(score.score))
        subject_stats[subject_name]['total'] += float(score.score)
        subject_stats[subject_name]['count'] += 1
    
    for subject in subject_stats:
        subject_stats[subject]['average'] = round(
            subject_stats[subject]['total'] / subject_stats[subject]['count'], 1
        )
    
    # 차트 데이터
    chart_data = {
        'labels': [s.exam.exam_date.strftime('%m/%d') for s in reversed(list(scores[:10]))],
        'scores': [float(s.score) for s in reversed(list(scores[:10]))],
    }
    
    return render(request, 'academics/student_scores.html', {
        'student': student,
        'scores': scores,
        'subject_stats': subject_stats,
        'chart_data': chart_data,
    })


@login_required
def student_scores_api(request, student_pk):
    """학생별 성적 차트 API"""
    student = get_object_or_404(Student, pk=student_pk)
    scores = student.scores.select_related('exam').order_by('exam__exam_date')[:20]
    
    return JsonResponse({
        'labels': [s.exam.exam_date.strftime('%Y-%m-%d') for s in scores],
        'data': [float(s.score) for s in scores],
        'exams': [s.exam.name for s in scores],
    })


@login_required
def subject_list(request):
    """과목 목록"""
    subjects = Subject.objects.all()
    return render(request, 'academics/subject_list.html', {'subjects': subjects})


@login_required
def subject_create(request):
    """과목 등록"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '과목이 등록되었습니다.')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'academics/subject_form.html', {
        'form': form,
        'title': '과목 등록',
    })


@login_required
def goal_list(request):
    """학습 목표 목록"""
    goals = LearningGoal.objects.select_related('student', 'subject').all()
    
    status = request.GET.get('status')
    if status:
        goals = goals.filter(status=status)
    
    return render(request, 'academics/goal_list.html', {
        'goals': goals,
        'status_choices': LearningGoal.STATUS_CHOICES,
    })


@login_required
def goal_create(request):
    """학습 목표 등록"""
    if request.method == 'POST':
        form = LearningGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()
            messages.success(request, '학습 목표가 등록되었습니다.')
            return redirect('academics:goal_list')
    else:
        initial = {}
        student_id = request.GET.get('student')
        if student_id:
            initial['student'] = student_id
        form = LearningGoalForm(initial=initial)
    
    return render(request, 'academics/goal_form.html', {
        'form': form,
        'title': '학습 목표 등록',
    })


@login_required
def report_card_list(request):
    """성적표 목록"""
    report_cards = ReportCard.objects.select_related('student').all()
    return render(request, 'academics/report_card_list.html', {
        'report_cards': report_cards,
    })


@login_required
def report_card_create(request):
    """성적표 생성"""
    if request.method == 'POST':
        form = ReportCardForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            
            # 통계 계산
            student = report.student
            scores = Score.objects.filter(
                student=student,
                exam__exam_date__gte=report.period_start,
                exam__exam_date__lte=report.period_end
            )
            report.total_exams = scores.count()
            avg = scores.aggregate(avg=Avg('score'))['avg']
            report.average_score = round(avg, 1) if avg else None
            
            report.save()
            messages.success(request, '성적표가 생성되었습니다.')
            return redirect('academics:report_card_list')
    else:
        form = ReportCardForm()
    
    return render(request, 'academics/report_card_form.html', {
        'form': form,
        'title': '성적표 생성',
    })


@login_required
def report_card_detail(request, pk):
    """성적표 상세"""
    report = get_object_or_404(ReportCard, pk=pk)
    
    # 해당 기간 성적
    scores = Score.objects.filter(
        student=report.student,
        exam__exam_date__gte=report.period_start,
        exam__exam_date__lte=report.period_end
    ).select_related('exam', 'exam__subject').order_by('exam__exam_date')
    
    return render(request, 'academics/report_card_detail.html', {
        'report': report,
        'scores': scores,
    })


@login_required
def report_card_pdf(request, pk):
    """성적표 PDF 다운로드"""
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    
    report = get_object_or_404(ReportCard, pk=pk)
    
    # 해당 기간 성적
    scores = Score.objects.filter(
        student=report.student,
        exam__exam_date__gte=report.period_start,
        exam__exam_date__lte=report.period_end
    ).select_related('exam', 'exam__subject').order_by('exam__exam_date')
    
    # 과목별 평균 계산
    subject_stats = {}
    for score in scores:
        subject_name = score.exam.subject.name if score.exam.subject else '기타'
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {'total': 0, 'count': 0}
        subject_stats[subject_name]['total'] += float(score.score)
        subject_stats[subject_name]['count'] += 1
    
    for subject in subject_stats:
        subject_stats[subject]['average'] = round(
            subject_stats[subject]['total'] / subject_stats[subject]['count'], 1
        )
    
    # HTML 렌더링
    html_content = render_to_string('academics/report_card_pdf.html', {
        'report': report,
        'scores': scores,
        'subject_stats': subject_stats,
        'generated_at': timezone.now(),
    })
    
    try:
        from weasyprint import HTML
        pdf = HTML(string=html_content).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"report_card_{report.student.name}_{report.period_end.strftime('%Y%m')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # 발급 완료 처리
        if not report.is_published:
            report.is_published = True
            report.published_at = timezone.now()
            report.save()
        
        return response
    except Exception as e:
        messages.error(request, f'PDF 생성 오류: {str(e)}')
        return redirect('academics:report_card_detail', pk=pk)

