from django.apps import AppConfig


class ExportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exports'
    verbose_name = '데이터 내보내기'
