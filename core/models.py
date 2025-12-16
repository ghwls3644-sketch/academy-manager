from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class MessageLog(models.Model):
    """SMS/알림톡 발송 기록"""
    TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('kakao', '카카오 알림톡'),
        ('email', '이메일'),
    ]
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('sent', '발송 완료'),
        ('failed', '발송 실패'),
        ('retry', '재시도'),
    ]
    
    message_type = models.CharField('메시지 유형', max_length=20, choices=TYPE_CHOICES)
    recipient = models.CharField('수신자', max_length=100)
    recipient_phone = models.CharField('수신 번호', max_length=20, blank=True)
    subject = models.CharField('제목', max_length=200, blank=True)
    content = models.TextField('내용')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('오류 메시지', blank=True)
    retry_count = models.PositiveIntegerField('재시도 횟수', default=0)
    sent_at = models.DateTimeField('발송 시각', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='발송자')
    
    class Meta:
        verbose_name = '메시지 로그'
        verbose_name_plural = '메시지 로그 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.get_message_type_display()}] {self.recipient} - {self.get_status_display()}"


class Notification(models.Model):
    """시스템 내부 알림"""
    TYPE_CHOICES = [
        ('info', '정보'),
        ('warning', '경고'),
        ('success', '성공'),
        ('error', '오류'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='사용자')
    title = models.CharField('제목', max_length=200)
    message = models.TextField('내용')
    notification_type = models.CharField('유형', max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField('읽음 여부', default=False)
    link = models.CharField('링크', max_length=200, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    read_at = models.DateTimeField('읽은 시각', null=True, blank=True)
    
    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.user.username}] {self.title}"


class SystemSetting(models.Model):
    """시스템 설정 (Key-Value)"""
    key = models.CharField('설정 키', max_length=100, unique=True)
    value = models.TextField('설정 값')
    description = models.CharField('설명', max_length=200, blank=True)
    is_active = models.BooleanField('활성화', default=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='수정자')
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '시스템 설정'
        verbose_name_plural = '시스템 설정 목록'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class Backup(models.Model):
    """백업 기록"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('running', '진행 중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    filename = models.CharField('파일명', max_length=200)
    file_path = models.CharField('파일 경로', max_length=500)
    file_size = models.BigIntegerField('파일 크기 (bytes)', default=0)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('오류 메시지', blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    completed_at = models.DateTimeField('완료 시각', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='생성자')
    
    class Meta:
        verbose_name = '백업'
        verbose_name_plural = '백업 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.filename} ({self.get_status_display()})"
