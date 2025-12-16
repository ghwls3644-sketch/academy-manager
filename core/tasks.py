"""
Core app Celery tasks.
비동기 작업 정의 (SMS 발송, 백업, 통계 집계 등)
"""

from celery import shared_task
from django.utils import timezone


@shared_task
def send_message_task(message_log_id):
    """메시지 발송 태스크 (SMS/알림톡)"""
    from .models import MessageLog
    
    try:
        message = MessageLog.objects.get(id=message_log_id)
        
        # TODO: 실제 발송 로직 구현 (SMS API 호출 등)
        # 현재는 성공으로 가정
        message.status = 'sent'
        message.sent_at = timezone.now()
        message.save()
        
        return {'status': 'success', 'message_id': message_log_id}
    
    except MessageLog.DoesNotExist:
        return {'status': 'error', 'message': 'Message not found'}
    except Exception as e:
        # 실패 시 재시도 카운트 증가
        message.status = 'failed'
        message.error_message = str(e)
        message.retry_count += 1
        message.save()
        raise  # Celery가 재시도하도록 예외 발생


@shared_task
def create_backup_task():
    """데이터베이스 백업 태스크"""
    import subprocess
    import os
    from django.conf import settings
    from .models import Backup
    
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.sql"
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # 백업 디렉토리 생성
    os.makedirs(backup_dir, exist_ok=True)
    file_path = os.path.join(backup_dir, filename)
    
    # 백업 레코드 생성
    backup = Backup.objects.create(
        filename=filename,
        file_path=file_path,
        status='running'
    )
    
    try:
        # TODO: Docker 환경에서 pg_dump 실행
        # subprocess.run(['pg_dump', ...])
        
        backup.status = 'completed'
        backup.completed_at = timezone.now()
        backup.save()
        
        return {'status': 'success', 'backup_id': backup.id}
    
    except Exception as e:
        backup.status = 'failed'
        backup.error_message = str(e)
        backup.save()
        return {'status': 'error', 'message': str(e)}


@shared_task
def calculate_monthly_statistics():
    """월별 통계 집계 태스크"""
    # TODO: 월별 출석률, 매출 등 통계 계산
    pass


@shared_task
def send_payment_reminders():
    """수납 알림 발송 태스크"""
    # TODO: 미납자 대상 자동 알림 발송
    pass
