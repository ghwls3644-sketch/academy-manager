"""
학부모 포털 뷰
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta

from .models import ParentAccount, ParentInvite, ParentMessage
from .forms import ParentRegistrationForm, ParentLoginForm, ParentMessageForm, ParentProfileForm
from students.models import Student
from attendance.models import Attendance
from payments.models import Payment
from academics.models import Score


def parent_required(view_func):
    """학부모 계정 필수 데코레이터"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('parent_portal:login')
        if not hasattr(request.user, 'parent_account'):
            messages.error(request, '학부모 계정이 아닙니다.')
            return redirect('parent_portal:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def parent_login(request):
    """학부모 로그인"""
    if request.user.is_authenticated and hasattr(request.user, 'parent_account'):
        return redirect('parent_portal:dashboard')
    
    if request.method == 'POST':
        form = ParentLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user and hasattr(user, 'parent_account'):
                login(request, user)
                user.parent_account.last_login_at = timezone.now()
                user.parent_account.save()
                return redirect('parent_portal:dashboard')
            else:
                messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    else:
        form = ParentLoginForm()
    
    return render(request, 'parent_portal/login.html', {'form': form})


def parent_logout(request):
    """학부모 로그아웃"""
    logout(request)
    return redirect('parent_portal:login')


def parent_register(request):
    """학부모 회원가입"""
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data['invite_code']
            
            # 초대 코드 확인
            try:
                invite = ParentInvite.objects.get(
                    code=invite_code,
                    status='pending',
                    expires_at__gt=timezone.now()
                )
            except ParentInvite.DoesNotExist:
                messages.error(request, '유효하지 않은 초대 코드입니다.')
                return render(request, 'parent_portal/register.html', {'form': form})
            
            # 사용자 생성
            user = form.save()
            
            # 학부모 계정 생성
            parent = ParentAccount.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data.get('email', ''),
                relationship=form.cleaned_data['relationship'],
            )
            parent.children.add(invite.student)
            
            # 초대 코드 사용 처리
            invite.status = 'used'
            invite.used_at = timezone.now()
            invite.used_by = parent
            invite.save()
            
            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('parent_portal:login')
    else:
        form = ParentRegistrationForm()
    
    return render(request, 'parent_portal/register.html', {'form': form})


@parent_required
def dashboard(request):
    """학부모 대시보드"""
    parent = request.user.parent_account
    children = parent.children.all()
    
    today = timezone.now().date()
    
    # 각 자녀별 정보
    children_info = []
    for child in children:
        # 최근 출결
        recent_attendance = Attendance.objects.filter(
            student=child,
            date__gte=today - timedelta(days=7)
        ).order_by('-date')[:5]
        
        # 이번달 수납
        current_month = today.month
        current_year = today.year
        payment = Payment.objects.filter(
            student=child,
            year=current_year,
            month=current_month
        ).first()
        
        # 최근 성적
        recent_scores = Score.objects.filter(
            student=child
        ).select_related('exam').order_by('-exam__exam_date')[:3]
        
        children_info.append({
            'student': child,
            'attendance': recent_attendance,
            'payment': payment,
            'scores': recent_scores,
        })
    
    # 읽지 않은 메시지
    unread_messages = ParentMessage.objects.filter(
        parent=parent,
        direction='to_parent',
        is_read=False
    ).count()
    
    return render(request, 'parent_portal/dashboard.html', {
        'parent': parent,
        'children_info': children_info,
        'unread_messages': unread_messages,
    })


@parent_required
def child_attendance(request, student_pk):
    """자녀 출결 조회"""
    parent = request.user.parent_account
    student = get_object_or_404(parent.children, pk=student_pk)
    
    # 월별 필터
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    attendances = Attendance.objects.filter(
        student=student,
        date__year=year,
        date__month=month
    ).order_by('-date')
    
    # 통계
    stats = {
        'total': attendances.count(),
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
    }
    
    return render(request, 'parent_portal/child_attendance.html', {
        'student': student,
        'attendances': attendances,
        'stats': stats,
        'year': year,
        'month': month,
    })


@parent_required
def child_scores(request, student_pk):
    """자녀 성적 조회"""
    parent = request.user.parent_account
    student = get_object_or_404(parent.children, pk=student_pk)
    
    scores = Score.objects.filter(
        student=student,
        exam__is_published=True  # 공개된 성적만
    ).select_related('exam', 'exam__subject').order_by('-exam__exam_date')
    
    # 과목별 평균
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
    
    return render(request, 'parent_portal/child_scores.html', {
        'student': student,
        'scores': scores,
        'subject_stats': subject_stats,
    })


@parent_required
def child_payments(request, student_pk):
    """자녀 수납 조회"""
    parent = request.user.parent_account
    student = get_object_or_404(parent.children, pk=student_pk)
    
    payments = Payment.objects.filter(student=student).order_by('-year', '-month')
    
    return render(request, 'parent_portal/child_payments.html', {
        'student': student,
        'payments': payments,
    })


@parent_required
def message_list(request):
    """메시지 목록"""
    parent = request.user.parent_account
    messages_list = ParentMessage.objects.filter(parent=parent).order_by('-created_at')
    
    return render(request, 'parent_portal/message_list.html', {
        'messages': messages_list,
    })


@parent_required
def message_create(request):
    """메시지 작성"""
    parent = request.user.parent_account
    
    if request.method == 'POST':
        form = ParentMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.parent = parent
            message.direction = 'to_academy'
            message.save()
            messages.success(request, '메시지가 전송되었습니다.')
            return redirect('parent_portal:message_list')
    else:
        form = ParentMessageForm()
        form.fields['student'].queryset = parent.children.all()
    
    return render(request, 'parent_portal/message_form.html', {
        'form': form,
    })


@parent_required
def message_detail(request, pk):
    """메시지 상세"""
    parent = request.user.parent_account
    message = get_object_or_404(ParentMessage, pk=pk, parent=parent)
    
    # 읽음 처리
    if not message.is_read and message.direction == 'to_parent':
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
    
    return render(request, 'parent_portal/message_detail.html', {
        'message': message,
    })


@parent_required
def profile(request):
    """프로필 수정"""
    parent = request.user.parent_account
    
    if request.method == 'POST':
        form = ParentProfileForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('parent_portal:dashboard')
    else:
        form = ParentProfileForm(instance=parent)
    
    return render(request, 'parent_portal/profile.html', {
        'form': form,
    })
