from django.urls import path
from . import views

app_name = 'parent_portal'

urlpatterns = [
    # 인증
    path('login/', views.parent_login, name='login'),
    path('logout/', views.parent_logout, name='logout'),
    path('register/', views.parent_register, name='register'),
    
    # 대시보드
    path('', views.dashboard, name='dashboard'),
    
    # 자녀 정보
    path('child/<int:student_pk>/attendance/', views.child_attendance, name='child_attendance'),
    path('child/<int:student_pk>/scores/', views.child_scores, name='child_scores'),
    path('child/<int:student_pk>/payments/', views.child_payments, name='child_payments'),
    
    # 메시지
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    
    # 프로필
    path('profile/', views.profile, name='profile'),
]
