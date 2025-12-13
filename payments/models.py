from django.db import models
from students.models import Student


class Payment(models.Model):
    """수납 기록"""
    STATUS_CHOICES = [
        ('paid', '완납'),
        ('unpaid', '미납'),
        ('partial', '부분납'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', '현금'),
        ('card', '카드'),
        ('transfer', '계좌이체'),
        ('other', '기타'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name='학생'
    )
    
    # 수납 정보
    year = models.IntegerField('년도')
    month = models.IntegerField('월')
    amount = models.PositiveIntegerField('청구 금액', default=0)
    paid_amount = models.PositiveIntegerField('납부 금액', default=0)
    
    status = models.CharField('납부 상태', max_length=20, choices=STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField('결제 방식', max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_date = models.DateField('납부일', null=True, blank=True)
    
    note = models.TextField('메모', blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '수납'
        verbose_name_plural = '수납 목록'
        ordering = ['-year', '-month', 'student__name']
        unique_together = ['student', 'year', 'month']
    
    def __str__(self):
        return f"{self.student.name} - {self.year}년 {self.month}월"
    
    @property
    def remaining_amount(self):
        """미납 금액"""
        return max(0, self.amount - self.paid_amount)
    
    def save(self, *args, **kwargs):
        # 자동 상태 업데이트
        if self.paid_amount >= self.amount and self.amount > 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        super().save(*args, **kwargs)
