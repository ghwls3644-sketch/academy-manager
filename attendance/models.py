from django.db import models
from students.models import Student
from classes.models import Class


class Attendance(models.Model):
    """출결 기록"""
    STATUS_CHOICES = [
        ('present', '출석'),
        ('absent', '결석'),
        ('late', '지각'),
        ('early_leave', '조퇴'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='attendances',
        verbose_name='학생'
    )
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        verbose_name='반'
    )
    date = models.DateField('날짜')
    status = models.CharField('출결 상태', max_length=20, choices=STATUS_CHOICES, default='present')
    note = models.TextField('메모', blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '출결'
        verbose_name_plural = '출결 목록'
        ordering = ['-date', 'student__name']
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.get_status_display()})"


class QrSession(models.Model):
    """QR 출석 세션"""
    STATUS_CHOICES = [
        ('active', '활성'),
        ('expired', '만료'),
        ('closed', '종료'),
    ]
    
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='qr_sessions',
        verbose_name='반'
    )
    lesson_date = models.DateField('수업일')
    token = models.CharField('토큰', max_length=64, unique=True)
    
    starts_at = models.DateTimeField('시작 시각')
    expires_at = models.DateTimeField('만료 시각')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='생성자'
    )
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = 'QR 세션'
        verbose_name_plural = 'QR 세션 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.assigned_class.name} - {self.lesson_date} ({self.get_status_display()})"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def check_and_expire(self):
        """만료 확인 및 상태 업데이트"""
        if self.status == 'active' and self.is_expired:
            self.status = 'expired'
            self.save()


class QrScanLog(models.Model):
    """QR 스캔 로그"""
    RESULT_CHOICES = [
        ('success', '성공'),
        ('fail', '실패'),
    ]
    FAIL_REASON_CHOICES = [
        ('invalid_token', '잘못된 토큰'),
        ('expired', '만료된 세션'),
        ('not_enrolled', '미등록 학생'),
        ('duplicate', '중복 출석'),
        ('unknown', '알 수 없음'),
    ]
    
    qr_session = models.ForeignKey(
        QrSession,
        on_delete=models.CASCADE,
        related_name='scan_logs',
        verbose_name='QR 세션'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_scans',
        verbose_name='학생'
    )
    
    scanned_at = models.DateTimeField('스캔 시각', auto_now_add=True)
    result = models.CharField('결과', max_length=20, choices=RESULT_CHOICES)
    fail_reason = models.CharField('실패 사유', max_length=30, choices=FAIL_REASON_CHOICES, blank=True)
    
    client_ip = models.GenericIPAddressField('클라이언트 IP', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    
    class Meta:
        verbose_name = 'QR 스캔 로그'
        verbose_name_plural = 'QR 스캔 로그 목록'
        ordering = ['-scanned_at']
    
    def __str__(self):
        student_name = self.student.name if self.student else '알 수 없음'
        return f"{student_name} - {self.get_result_display()}"
