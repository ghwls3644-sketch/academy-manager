from django.db import models
from django.contrib.auth.models import User
from classes.models import Class
from teachers.models import Teacher


class CalendarEvent(models.Model):
    """캘린더 이벤트"""
    TYPE_CHOICES = [
        ('class', '정규 수업'),
        ('makeup', '보강'),
        ('holiday', '휴원'),
        ('special', '특강'),
        ('camp', '캠프'),
        ('other', '기타'),
    ]
    
    title = models.CharField('제목', max_length=200)
    event_type = models.CharField('유형', max_length=20, choices=TYPE_CHOICES, default='class')
    description = models.TextField('설명', blank=True)
    
    start_date = models.DateField('시작일')
    end_date = models.DateField('종료일', null=True, blank=True)
    start_time = models.TimeField('시작 시간', null=True, blank=True)
    end_time = models.TimeField('종료 시간', null=True, blank=True)
    all_day = models.BooleanField('종일', default=False)
    
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events',
        verbose_name='반'
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_events',
        verbose_name='담당 강사'
    )
    
    location = models.CharField('장소', max_length=200, blank=True)
    color = models.CharField('색상', max_length=7, default='#4285f4')
    
    is_recurring = models.BooleanField('반복 여부', default=False)
    recurrence_rule = models.CharField('반복 규칙', max_length=200, blank=True,
                                        help_text='RRULE 형식 (예: FREQ=WEEKLY;BYDAY=MO,WE,FR)')
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events',
        verbose_name='생성자'
    )
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '캘린더 이벤트'
        verbose_name_plural = '캘린더 이벤트 목록'
        ordering = ['start_date', 'start_time']
    
    def __str__(self):
        return f"[{self.get_event_type_display()}] {self.title}"


class MakeupClass(models.Model):
    """보강 수업"""
    STATUS_CHOICES = [
        ('scheduled', '예정'),
        ('completed', '완료'),
        ('cancelled', '취소'),
    ]
    
    original_date = models.DateField('원래 수업일')
    original_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='makeup_classes',
        verbose_name='원래 반'
    )
    
    makeup_event = models.OneToOneField(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='makeup_info',
        verbose_name='보강 일정'
    )
    
    reason = models.TextField('보강 사유')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='생성자'
    )
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '보강 수업'
        verbose_name_plural = '보강 수업 목록'
        ordering = ['-original_date']
    
    def __str__(self):
        return f"{self.original_class.name} 보강 ({self.original_date})"


class HolidayRange(models.Model):
    """휴원 기간"""
    TYPE_CHOICES = [
        ('regular', '정기 휴원'),
        ('national', '공휴일'),
        ('temporary', '임시 휴원'),
        ('other', '기타'),
    ]
    
    title = models.CharField('제목', max_length=200)
    holiday_type = models.CharField('유형', max_length=20, choices=TYPE_CHOICES, default='regular')
    start_date = models.DateField('시작일')
    end_date = models.DateField('종료일')
    description = models.TextField('설명', blank=True)
    
    affects_all = models.BooleanField('전체 적용', default=True)
    affected_classes = models.ManyToManyField(
        Class,
        blank=True,
        related_name='holidays',
        verbose_name='적용 반'
    )
    
    notify_parents = models.BooleanField('학부모 알림', default=True)
    notified_at = models.DateTimeField('알림 발송일', null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='생성자'
    )
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '휴원 기간'
        verbose_name_plural = '휴원 기간 목록'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} ({self.start_date} ~ {self.end_date})"
    
    @property
    def duration_days(self):
        """휴원 기간 일수"""
        return (self.end_date - self.start_date).days + 1
