from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    path('', views.export_hub, name='hub'),
    path('students/', views.export_students, name='students'),
    path('attendance/', views.export_attendance, name='attendance'),
    path('payments/', views.export_payments, name='payments'),
]
