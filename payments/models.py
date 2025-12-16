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


class Discount(models.Model):
    """할인/장학금 정책"""
    TYPE_CHOICES = [
        ('sibling', '형제 할인'),
        ('scholarship', '장학금'),
        ('early_bird', '조기 등록 할인'),
        ('referral', '추천인 할인'),
        ('other', '기타'),
    ]
    
    name = models.CharField('할인명', max_length=100)
    discount_type = models.CharField('할인 유형', max_length=20, choices=TYPE_CHOICES)
    discount_rate = models.DecimalField('할인율 (%)', max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.PositiveIntegerField('할인 금액', null=True, blank=True)
    description = models.TextField('설명', blank=True)
    is_active = models.BooleanField('활성화', default=True)
    start_date = models.DateField('시작일', null=True, blank=True)
    end_date = models.DateField('종료일', null=True, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '할인 정책'
        verbose_name_plural = '할인 정책 목록'
    
    def __str__(self):
        if self.discount_rate:
            return f"{self.name} ({self.discount_rate}%)"
        return f"{self.name} ({self.discount_amount:,}원)"


class StudentDiscount(models.Model):
    """학생별 적용된 할인"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discounts', verbose_name='학생')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, verbose_name='할인 정책')
    applied_date = models.DateField('적용일', auto_now_add=True)
    note = models.CharField('비고', max_length=200, blank=True)
    
    class Meta:
        verbose_name = '학생 할인'
        verbose_name_plural = '학생 할인 목록'
        unique_together = ['student', 'discount']
    
    def __str__(self):
        return f"{self.student.name} - {self.discount.name}"


class Refund(models.Model):
    """환불 기록"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('approved', '승인'),
        ('completed', '완료'),
        ('rejected', '거절'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='refunds', verbose_name='학생')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='관련 수납')
    
    refund_amount = models.PositiveIntegerField('환불 금액')
    reason = models.TextField('환불 사유')
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    requested_at = models.DateTimeField('요청일', auto_now_add=True)
    processed_at = models.DateTimeField('처리일', null=True, blank=True)
    processed_by = models.CharField('처리자', max_length=100, blank=True)
    
    bank_name = models.CharField('은행명', max_length=50, blank=True)
    account_number = models.CharField('계좌번호', max_length=50, blank=True)
    account_holder = models.CharField('예금주', max_length=50, blank=True)
    
    note = models.TextField('비고', blank=True)
    
    class Meta:
        verbose_name = '환불'
        verbose_name_plural = '환불 목록'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.refund_amount:,}원 ({self.get_status_display()})"
