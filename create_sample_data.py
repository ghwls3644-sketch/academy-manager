import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Role, Employee
from teachers.models import Teacher
from students.models import Student
from datetime import date
import random

# 강사 역할 생성 또는 가져오기
teacher_role, _ = Role.objects.get_or_create(name='teacher', defaults={'description': '강사'})

# 강사 데이터
teacher_data = [
    {'first_name': '민준', 'last_name': '김', 'subject': '수학', 'username': 'teacher_kim'},
    {'first_name': '서연', 'last_name': '이', 'subject': '영어', 'username': 'teacher_lee'},
    {'first_name': '지훈', 'last_name': '박', 'subject': '국어', 'username': 'teacher_park'},
]

for data in teacher_data:
    if not User.objects.filter(username=data['username']).exists():
        user = User.objects.create_user(
            username=data['username'],
            password='1234',
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        employee = Employee.objects.create(
            user=user,
            role=teacher_role,
            phone=f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
            hire_date=date(2024, random.randint(1,12), random.randint(1,28))
        )
        Teacher.objects.create(
            employee=employee,
            subject=data['subject'],
            bio=f'{data["last_name"]}{data["first_name"]} 강사입니다.'
        )
        print(f'강사 생성: {data["last_name"]}{data["first_name"]}')
    else:
        print(f'강사 이미 존재: {data["last_name"]}{data["first_name"]}')

# 학생 데이터
student_names = [
    ('하준', 'M'), ('서윤', 'F'), ('도윤', 'M'), ('하은', 'F'), ('시우', 'M'),
    ('지아', 'F'), ('주원', 'M'), ('서아', 'F'), ('지호', 'M'), ('민서', 'F')
]
last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임']
grades = ['초1', '초2', '초3', '초4', '초5', '초6', '중1', '중2', '중3']
schools = ['서울초등학교', '강남초등학교', '송파초등학교', '한강초등학교']

for i, (first_name, gender) in enumerate(student_names):
    last_name = last_names[i % len(last_names)]
    full_name = f'{last_name}{first_name}'
    if not Student.objects.filter(name=full_name).exists():
        Student.objects.create(
            name=full_name,
            gender=gender,
            birth_date=date(2010 + random.randint(0,8), random.randint(1,12), random.randint(1,28)),
            phone=f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
            parent_name=f'{last_name}부모',
            parent_phone=f'010-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
            parent_relation=random.choice(['어머니', '아버지']),
            school_name=random.choice(schools),
            grade=random.choice(grades),
            enrollment_date=date(2024, random.randint(1,12), random.randint(1,28))
        )
        print(f'학생 생성: {full_name}')
    else:
        print(f'학생 이미 존재: {full_name}')

print('\n=== 완료 ===')
print(f'강사 수: {Teacher.objects.count()}')
print(f'학생 수: {Student.objects.count()}')
