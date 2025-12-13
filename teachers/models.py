from django.db import models
from accounts.models import Employee


class Teacher(models.Model):
    """강사 정보"""
    employee = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile',
        verbose_name='직원'
    )
    subject = models.CharField('담당 과목', max_length=100, blank=True)
    bio = models.TextField('소개', blank=True)
    is_active = models.BooleanField('활성 여부', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '강사'
        verbose_name_plural = '강사 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return str(self.employee)
    
    @property
    def name(self):
        return str(self.employee)
    
    @property
    def phone(self):
        return self.employee.phone
    
    @property
    def email(self):
        return self.employee.user.email
