from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('send/', views.message_send, name='send'),
    path('logs/', views.message_logs, name='logs'),
]
