from django.db import models
from teachers.models import Teacher


class Class(models.Model):
    """반 정보"""
    WEEKDAY_CHOICES = [
        ('mon', '월'),
        ('tue', '화'),
        ('wed', '수'),
        ('thu', '목'),
        ('fri', '금'),
        ('sat', '토'),
        ('sun', '일'),
    ]
    
    name = models.CharField('반 이름', max_length=100)
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='classes',
        verbose_name='담당 강사'
    )
    subject = models.CharField('과목', max_length=100, blank=True)
    description = models.TextField('설명', blank=True)
    
    # 수업 일정
    weekdays = models.CharField('수업 요일', max_length=50, blank=True, 
                                 help_text='쉼표로 구분 (예: mon,wed,fri)')
    start_time = models.TimeField('시작 시간', null=True, blank=True)
    end_time = models.TimeField('종료 시간', null=True, blank=True)
    
    max_students = models.PositiveIntegerField('정원', default=20)
    monthly_fee = models.PositiveIntegerField('월 수강료', default=0)
    
    is_active = models.BooleanField('활성 여부', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '반'
        verbose_name_plural = '반 목록'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def student_count(self):
        """현재 수강 학생 수"""
        return self.students.filter(status='enrolled').count()
    
    @property
    def weekday_display(self):
        """수업 요일 표시"""
        if not self.weekdays:
            return '-'
        weekday_dict = dict(self.WEEKDAY_CHOICES)
        days = [weekday_dict.get(d.strip(), d) for d in self.weekdays.split(',')]
        return ', '.join(days)
    
    @property
    def schedule_display(self):
        """수업 시간 표시"""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        return '-'
