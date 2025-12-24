"""
Core utility functions for Academy Manager
공통으로 사용되는 유틸리티 함수들
"""
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_year_choices(range_back=2, range_forward=2):
    """
    년도 선택 목록 생성
    
    Args:
        range_back: 현재 년도 기준 과거 범위
        range_forward: 현재 년도 기준 미래 범위
    
    Returns:
        list: 년도 목록
    """
    current_year = timezone.now().year
    return list(range(current_year - range_back, current_year + range_forward))


def parse_date_safe(date_str, default=None, date_format='%Y-%m-%d'):
    """
    안전한 날짜 파싱
    
    Args:
        date_str: 날짜 문자열
        default: 파싱 실패 시 기본값 (None이면 오늘 날짜)
        date_format: 날짜 형식
    
    Returns:
        date: 파싱된 날짜 또는 기본값
    """
    if not date_str:
        return default or timezone.now().date()
    try:
        return datetime.strptime(date_str, date_format).date()
    except ValueError:
        logger.warning(f"날짜 파싱 실패: {date_str}")
        return default or timezone.now().date()


def get_month_choices():
    """
    월 선택 목록 생성
    
    Returns:
        list: (value, label) 튜플 목록
    """
    return [
        ('', '전체'),
        ('1', '1월'), ('2', '2월'), ('3', '3월'),
        ('4', '4월'), ('5', '5월'), ('6', '6월'),
        ('7', '7월'), ('8', '8월'), ('9', '9월'),
        ('10', '10월'), ('11', '11월'), ('12', '12월'),
    ]


def format_phone(phone):
    """
    전화번호 포맷팅
    
    Args:
        phone: 전화번호 문자열
    
    Returns:
        str: 포맷된 전화번호 (예: 010-1234-5678)
    """
    if not phone:
        return ''
    
    # 숫자만 추출
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 11:  # 휴대폰
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10:  # 지역번호 (02 등)
        if digits.startswith('02'):
            return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    
    return phone  # 원본 반환


def format_currency(amount):
    """
    금액 포맷팅
    
    Args:
        amount: 금액 (정수 또는 None)
    
    Returns:
        str: 포맷된 금액 (예: 150,000원)
    """
    if amount is None:
        return '0원'
    return f"{int(amount):,}원"
