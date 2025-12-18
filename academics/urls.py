from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # 시험
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:pk>/update/', views.exam_update, name='exam_update'),
    
    # 성적
    path('exams/<int:exam_pk>/scores/create/', views.score_create, name='score_create'),
    path('exams/<int:exam_pk>/scores/bulk/', views.score_bulk_create, name='score_bulk_create'),
    
    # 학생별 성적
    path('students/<int:student_pk>/scores/', views.student_scores, name='student_scores'),
    path('students/<int:student_pk>/scores/api/', views.student_scores_api, name='student_scores_api'),
    
    # 과목
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    
    # 학습 목표
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    
    # 성적표
    path('reports/', views.report_card_list, name='report_card_list'),
    path('reports/create/', views.report_card_create, name='report_card_create'),
    path('reports/<int:pk>/', views.report_card_detail, name='report_card_detail'),
    path('reports/<int:pk>/pdf/', views.report_card_pdf, name='report_card_pdf'),
]
