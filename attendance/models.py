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
