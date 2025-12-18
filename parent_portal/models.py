from django.db import models
from django.contrib.auth.models import User
from students.models import Student
import secrets
import string


class ParentAccount(models.Model):
    """학부모 계정"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_account',
        verbose_name='사용자'
    )
    
    # 연결된 자녀
    children = models.ManyToManyField(
        Student,
        related_name='parent_accounts',
        verbose_name='자녀'
    )
    
    name = models.CharField('이름', max_length=50)
    phone = models.CharField('연락처', max_length=20)
    email = models.EmailField('이메일', blank=True)
    relationship = models.CharField('관계', max_length=20, default='부모', 
                                    help_text='예: 아버지, 어머니, 조부모 등')
    
    # 알림 설정
    receive_attendance_alert = models.BooleanField('출결 알림 수신', default=True)
    receive_payment_alert = models.BooleanField('수납 알림 수신', default=True)
    receive_score_alert = models.BooleanField('성적 알림 수신', default=True)
    
    is_active = models.BooleanField('활성', default=True)
    last_login_at = models.DateTimeField('마지막 로그인', null=True, blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '학부모 계정'
        verbose_name_plural = '학부모 계정 목록'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.phone})"


class ParentInvite(models.Model):
    """학부모 초대 코드"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('used', '사용됨'),
        ('expired', '만료'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='parent_invites',
        verbose_name='학생'
    )
    
    code = models.CharField('초대 코드', max_length=20, unique=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    expires_at = models.DateTimeField('만료일시')
    used_at = models.DateTimeField('사용일시', null=True, blank=True)
    used_by = models.ForeignKey(
        ParentAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='사용자'
    )
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='생성자')
    
    class Meta:
        verbose_name = '학부모 초대'
        verbose_name_plural = '학부모 초대 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.name} 초대 - {self.code}"
    
    @classmethod
    def generate_code(cls):
        """초대 코드 생성"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(8))
            if not cls.objects.filter(code=code).exists():
                return code


class ParentMessage(models.Model):
    """학부모-학원 메시지"""
    DIRECTION_CHOICES = [
        ('to_academy', '학원으로'),
        ('to_parent', '학부모에게'),
    ]
    
    parent = models.ForeignKey(
        ParentAccount,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='학부모'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='parent_messages',
        verbose_name='학생'
    )
    
    direction = models.CharField('방향', max_length=20, choices=DIRECTION_CHOICES)
    subject = models.CharField('제목', max_length=200)
    content = models.TextField('내용')
    
    is_read = models.BooleanField('읽음', default=False)
    read_at = models.DateTimeField('읽은 시각', null=True, blank=True)
    
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '학부모 메시지'
        verbose_name_plural = '학부모 메시지 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.parent.name} - {self.subject}"
