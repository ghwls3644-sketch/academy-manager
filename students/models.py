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
