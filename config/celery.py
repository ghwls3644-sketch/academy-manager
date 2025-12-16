"""
Celery 설정 for Academy Manager project.
"""

import os
from celery import Celery

# Django settings 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Django settings에서 CELERY_ 접두어로 시작하는 설정 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# 모든 등록된 Django 앱에서 tasks.py 자동 탐색
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """디버그용 테스트 태스크"""
    print(f'Request: {self.request!r}')
