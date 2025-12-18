from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from classes.models import Class
from teachers.models import Teacher


class Subject(models.Model):
    """과목"""
    name = models.CharField('과목명', max_length=100)
    code = models.CharField('코드', max_length=20, unique=True)
    description = models.TextField('설명', blank=True)
    is_active = models.BooleanField('활성', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '과목'
        verbose_name_plural = '과목 목록'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Exam(models.Model):
    """시험"""
    TYPE_CHOICES = [
        ('monthly', '월간 테스트'),
        ('midterm', '중간고사'),
        ('final', '기말고사'),
        ('mock', '모의고사'),
        ('quiz', '쪽지시험'),
        ('other', '기타'),
    ]
    
    name = models.CharField('시험명', max_length=200)
    exam_type = models.CharField('유형', max_length=20, choices=TYPE_CHOICES, default='monthly')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        verbose_name='과목'
    )
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        verbose_name='대상 반'
    )
    
    exam_date = models.DateField('시험일')
    max_score = models.PositiveIntegerField('만점', default=100)
    
    description = models.TextField('설명', blank=True)
    is_published = models.BooleanField('공개 여부', default=False, help_text='학부모에게 공개')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='등록자')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '시험'
        verbose_name_plural = '시험 목록'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.name} ({self.exam_date})"
    
    @property
    def average_score(self):
        """평균 점수"""
        scores = self.scores.all()
        if not scores:
            return 0
        total = sum(s.score for s in scores)
        return round(total / len(scores), 1)
    
    @property
    def student_count(self):
        """응시 학생 수"""
        return self.scores.count()


class Score(models.Model):
    """성적"""
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D+', 'D+'), ('D', 'D'), ('D-', 'D-'),
        ('F', 'F'),
    ]
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name='시험'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name='학생'
    )
    
    score = models.DecimalField('점수', max_digits=5, decimal_places=1)
    grade = models.CharField('등급', max_length=2, choices=GRADE_CHOICES, blank=True)
    rank = models.PositiveIntegerField('순위', null=True, blank=True)
    
    feedback = models.TextField('피드백', blank=True)
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '성적'
        verbose_name_plural = '성적 목록'
        unique_together = ['exam', 'student']
        ordering = ['-exam__exam_date', 'student__name']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.score}점"
    
    @property
    def percentage(self):
        """백분율"""
        if self.exam.max_score:
            return round(float(self.score) / self.exam.max_score * 100, 1)
        return 0
    
    def save(self, *args, **kwargs):
        # 자동 등급 계산
        if not self.grade and self.exam.max_score:
            pct = self.percentage
            if pct >= 97: self.grade = 'A+'
            elif pct >= 93: self.grade = 'A'
            elif pct >= 90: self.grade = 'A-'
            elif pct >= 87: self.grade = 'B+'
            elif pct >= 83: self.grade = 'B'
            elif pct >= 80: self.grade = 'B-'
            elif pct >= 77: self.grade = 'C+'
            elif pct >= 73: self.grade = 'C'
            elif pct >= 70: self.grade = 'C-'
            elif pct >= 67: self.grade = 'D+'
            elif pct >= 63: self.grade = 'D'
            elif pct >= 60: self.grade = 'D-'
            else: self.grade = 'F'
        super().save(*args, **kwargs)


class LearningGoal(models.Model):
    """학습 목표"""
    STATUS_CHOICES = [
        ('active', '진행 중'),
        ('achieved', '달성'),
        ('failed', '미달성'),
        ('cancelled', '취소'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='learning_goals',
        verbose_name='학생'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='과목'
    )
    
    title = models.CharField('목표', max_length=200)
    description = models.TextField('상세 설명', blank=True)
    target_score = models.PositiveIntegerField('목표 점수', null=True, blank=True)
    
    start_date = models.DateField('시작일')
    end_date = models.DateField('종료일')
    
    current_progress = models.PositiveIntegerField('진행률 (%)', default=0)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='설정자')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '학습 목표'
        verbose_name_plural = '학습 목표 목록'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.title}"


class ReportCard(models.Model):
    """성적표"""
    PERIOD_CHOICES = [
        ('monthly', '월간'),
        ('quarterly', '분기'),
        ('semester', '학기'),
        ('yearly', '연간'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='report_cards',
        verbose_name='학생'
    )
    
    period_type = models.CharField('기간 유형', max_length=20, choices=PERIOD_CHOICES, default='monthly')
    period_start = models.DateField('시작일')
    period_end = models.DateField('종료일')
    title = models.CharField('제목', max_length=200)
    
    # 통계
    total_exams = models.PositiveIntegerField('시험 수', default=0)
    average_score = models.DecimalField('평균 점수', max_digits=5, decimal_places=1, null=True, blank=True)
    
    teacher_comment = models.TextField('강사 코멘트', blank=True)
    
    # PDF
    pdf_file = models.FileField('PDF 파일', upload_to='report_cards/', blank=True)
    is_published = models.BooleanField('발급 완료', default=False)
    published_at = models.DateTimeField('발급일', null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='생성자')
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    
    class Meta:
        verbose_name = '성적표'
        verbose_name_plural = '성적표 목록'
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.student.name} - {self.title}"
