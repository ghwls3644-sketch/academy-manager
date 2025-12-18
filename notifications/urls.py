from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # 템플릿 관리
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/update/', views.template_update, name='template_update'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('templates/preview/', views.template_preview, name='template_preview'),
    
    # 알림 발송
    path('send/', views.send_notification, name='send'),
    
    # 발송 작업
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    
    # 주간/월간 보고서
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/edit/', views.report_edit, name='report_edit'),
]
