from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    """사용자 역할 (관리자/강사)"""
    ROLE_CHOICES = [
        ('admin', '관리자'),
        ('teacher', '강사'),
    ]
    
    name = models.CharField('역할명', max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField('설명', blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '역할'
        verbose_name_plural = '역할 목록'
    
    def __str__(self):
        return self.get_name_display()


class Employee(models.Model):
    """직원 (강사/관리자) 정보"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name='역할')
    phone = models.CharField('연락처', max_length=20, blank=True)
    hire_date = models.DateField('입사일', null=True, blank=True)
    is_active = models.BooleanField('활성 여부', default=True)
    profile_image = models.ImageField('프로필 이미지', upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '직원'
        verbose_name_plural = '직원 목록'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def is_admin(self):
        return self.role and self.role.name == 'admin'
    
    @property
    def is_teacher(self):
        return self.role and self.role.name == 'teacher'
