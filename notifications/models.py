from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from classes.models import Class


class NotificationTemplate(models.Model):
    """알림 템플릿"""
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('kakao', '카카오 알림톡'),
        ('email', '이메일'),
        ('app', '앱 푸시'),
    ]
    
    TRIGGER_CHOICES = [
        ('manual', '수동 발송'),
        ('unpaid', '미납 알림'),
        ('absent', '결석 알림'),
        ('consult_reminder', '상담 리마인더'),
        ('schedule_change', '일정 변경'),
        ('enrollment', '등록 완료'),
        ('payment_complete', '수납 완료'),
    ]
    
    name = models.CharField('템플릿명', max_length=100)
    code = models.CharField('코드', max_length=50, unique=True, help_text='시스템 식별용 코드')
    channel = models.CharField('발송 채널', max_length=20, choices=CHANNEL_CHOICES, default='sms')
    trigger_type = models.CharField('트리거 유형', max_length=30, choices=TRIGGER_CHOICES, default='manual')
    
    subject = models.CharField('제목', max_length=200, blank=True, help_text='이메일 발송 시 사용')
    content = models.TextField('내용', help_text='변수: {학생명}, {반명}, {금액}, {마감일}, {날짜} 등')
    
    # 자동 발송 설정
    auto_send = models.BooleanField('자동 발송', default=False)
    days_before = models.IntegerField('N일 전 발송', null=True, blank=True, help_text='마감일 N일 전 자동 발송')
    send_time = models.TimeField('발송 시각', null=True, blank=True)
    
    is_active = models.BooleanField('활성화', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='생성자')
    
    class Meta:
        verbose_name = '알림 템플릿'
        verbose_name_plural = '알림 템플릿 목록'
        ordering = ['trigger_type', 'name']
    
    def __str__(self):
        return f"[{self.get_channel_display()}] {self.name}"


class NotificationJob(models.Model):
    """알림 발송 작업"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('processing', '처리중'),
        ('sent', '발송완료'),
        ('failed', '실패'),
        ('cancelled', '취소'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('student', '학생'),
        ('parent', '학부모'),
        ('class', '반 전체'),
        ('all', '전체'),
    ]
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='jobs',
        verbose_name='템플릿'
    )
    
    # 발송 대상
    target_type = models.CharField('대상 유형', max_length=20, choices=TARGET_TYPE_CHOICES, default='student')
    target_students = models.ManyToManyField(
        Student,
        blank=True,
        related_name='notification_jobs',
        verbose_name='대상 학생'
    )
    target_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='대상 반'
    )
    
    # 발송 내용
    subject = models.CharField('제목', max_length=200, blank=True)
    content = models.TextField('내용')
    
    # 발송 설정
    scheduled_at = models.DateTimeField('예약 발송일시', null=True, blank=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 결과
    total_count = models.IntegerField('전체 건수', default=0)
    success_count = models.IntegerField('성공 건수', default=0)
    fail_count = models.IntegerField('실패 건수', default=0)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    processed_at = models.DateTimeField('처리일', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='생성자')
    
    class Meta:
        verbose_name = '알림 발송 작업'
        verbose_name_plural = '알림 발송 작업 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class NotificationLog(models.Model):
    """알림 발송 로그"""
    RESULT_CHOICES = [
        ('success', '성공'),
        ('failed', '실패'),
    ]
    
    job = models.ForeignKey(
        NotificationJob,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='발송 작업'
    )
    
    recipient_name = models.CharField('수신자명', max_length=100)
    recipient_contact = models.CharField('수신 연락처', max_length=100)
    
    sent_content = models.TextField('발송 내용')
    result = models.CharField('결과', max_length=20, choices=RESULT_CHOICES)
    error_message = models.TextField('오류 메시지', blank=True)
    
    sent_at = models.DateTimeField('발송 시각', auto_now_add=True)
    provider_response = models.TextField('발송 응답', blank=True)
    
    class Meta:
        verbose_name = '알림 발송 로그'
        verbose_name_plural = '알림 발송 로그 목록'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient_name} - {self.get_result_display()}"


class WeeklyReport(models.Model):
    """주간/월간 보고서"""
    PERIOD_CHOICES = [
        ('weekly', '주간'),
        ('monthly', '월간'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '작성중'),
        ('ready', '발송대기'),
        ('sent', '발송완료'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='weekly_reports',
        verbose_name='학생'
    )
    
    period_type = models.CharField('기간유형', max_length=20, choices=PERIOD_CHOICES, default='weekly')
    start_date = models.DateField('시작일')
    end_date = models.DateField('종료일')
    
    title = models.CharField('제목', max_length=200)
    
    # 출결 통계
    attendance_total = models.IntegerField('총 수업일', default=0)
    attendance_present = models.IntegerField('출석', default=0)
    attendance_absent = models.IntegerField('결석', default=0)
    attendance_late = models.IntegerField('지각', default=0)
    
    # 성적 통계
    exam_count = models.IntegerField('시험 수', default=0)
    average_score = models.DecimalField('평균 점수', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 내용
    learning_summary = models.TextField('학습 내용', blank=True)
    teacher_comment = models.TextField('강사 코멘트', blank=True)
    homework_status = models.TextField('과제 현황', blank=True)
    next_plan = models.TextField('다음주 계획', blank=True)
    
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField('발송일시', null=True, blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    
    class Meta:
        verbose_name = '주간/월간 보고서'
        verbose_name_plural = '주간/월간 보고서 목록'
        ordering = ['-end_date', 'student']
    
    def __str__(self):
        return f"{self.student.name} - {self.title}"
    
    def calculate_stats(self):
        """통계 자동 계산"""
        from django.db.models import Avg
        from attendance.models import Attendance
        from academics.models import Score
        
        # 출결 통계
        attendances = Attendance.objects.filter(
            student=self.student,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        self.attendance_total = attendances.count()
        self.attendance_present = attendances.filter(status='present').count()
        self.attendance_absent = attendances.filter(status='absent').count()
        self.attendance_late = attendances.filter(status='late').count()
        
        # 성적 통계
        scores = Score.objects.filter(
            student=self.student,
            exam__exam_date__gte=self.start_date,
            exam__exam_date__lte=self.end_date
        )
        self.exam_count = scores.count()
        avg = scores.aggregate(avg=Avg('score'))['avg']
        self.average_score = round(avg, 2) if avg else None
    
    @property
    def attendance_rate(self):
        if self.attendance_total > 0:
            return round((self.attendance_present / self.attendance_total) * 100, 1)
        return 0

