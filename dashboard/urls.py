from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('api/attendance/', views.dashboard_attendance_api, name='api_attendance'),
    path('api/revenue/', views.dashboard_revenue_api, name='api_revenue'),
]
