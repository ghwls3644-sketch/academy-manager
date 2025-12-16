from django.urls import path
from . import views
from . import qr_views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('create/', views.attendance_create, name='create'),
    path('bulk/', views.attendance_bulk, name='bulk'),
    path('<int:pk>/edit/', views.attendance_update, name='update'),
    path('<int:pk>/delete/', views.attendance_delete, name='delete'),
    
    # QR 출석
    path('qr/generate/', qr_views.qr_generate, name='qr_generate'),
    path('qr/scan/', qr_views.qr_scan, name='qr_scan'),
    path('qr/scan/api/', qr_views.qr_scan_api, name='qr_scan_api'),
    path('qr/logs/', qr_views.qr_logs, name='qr_logs'),
]
