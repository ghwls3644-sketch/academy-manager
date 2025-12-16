from django.db import models
from classes.models import Class


class Student(models.Model):
    """학생 정보"""
    STATUS_CHOICES = [
        ('enrolled', '재원'),
        ('paused', '휴원'),
        ('withdrawn', '퇴원'),
    ]
    
    GENDER_CHOICES = [
        ('M', '남'),
        ('F', '여'),
    ]
    
    name = models.CharField('이름', max_length=50)
    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField('생년월일', null=True, blank=True)
    phone = models.CharField('연락처', max_length=20, blank=True)
    
    # 학부모 정보
    parent_name = models.CharField('학부모 이름', max_length=50, blank=True)
    parent_phone = models.CharField('학부모 연락처', max_length=20, blank=True)
    parent_relation = models.CharField('관계', max_length=20, blank=True, help_text='예: 어머니, 아버지')
    
    # 학원 정보
    assigned_class = models.ForeignKey(
        Class, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students',
        verbose_name='반'
    )
    status = models.CharField('재원 상태', max_length=20, choices=STATUS_CHOICES, default='enrolled')
    enrollment_date = models.DateField('등록일', null=True, blank=True)
    withdrawal_date = models.DateField('퇴원일', null=True, blank=True)
    
    school_name = models.CharField('학교명', max_length=100, blank=True)
    grade = models.CharField('학년', max_length=20, blank=True)
    
    note = models.TextField('메모', blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '학생'
        verbose_name_plural = '학생 목록'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class Waitlist(models.Model):
    """대기자 명단"""
    STATUS_CHOICES = [
        ('waiting', '대기 중'),
        ('contacted', '연락 완료'),
        ('enrolled', '등록 완료'),
        ('cancelled', '취소'),
    ]
    
    name = models.CharField('이름', max_length=50)
    phone = models.CharField('연락처', max_length=20)
    parent_name = models.CharField('학부모 이름', max_length=50, blank=True)
    parent_phone = models.CharField('학부모 연락처', max_length=20, blank=True)
    
    desired_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='희망 반'
    )
    desired_start_date = models.DateField('희망 시작일', null=True, blank=True)
    
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='waiting')
    priority = models.PositiveIntegerField('우선순위', default=0)
    note = models.TextField('메모', blank=True)
    
    registered_at = models.DateTimeField('등록일', auto_now_add=True)
    contacted_at = models.DateTimeField('연락일', null=True, blank=True)
    
    class Meta:
        verbose_name = '대기자'
        verbose_name_plural = '대기자 목록'
        ordering = ['priority', 'registered_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ConsultLog(models.Model):
    """상담 일지"""
    TYPE_CHOICES = [
        ('phone', '전화 상담'),
        ('visit', '방문 상담'),
        ('online', '온라인 상담'),
        ('other', '기타'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='consult_logs',
        verbose_name='학생'
    )
    
    consult_type = models.CharField('상담 유형', max_length=20, choices=TYPE_CHOICES)
    consult_date = models.DateField('상담일')
    counselor = models.CharField('상담자', max_length=50)
    
    topic = models.CharField('상담 주제', max_length=200)
    content = models.TextField('상담 내용')
    action_plan = models.TextField('후속 조치', blank=True)
    
    next_consult_date = models.DateField('다음 상담 예정일', null=True, blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '상담 일지'
        verbose_name_plural = '상담 일지 목록'
        ordering = ['-consult_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.consult_date} ({self.topic})"
