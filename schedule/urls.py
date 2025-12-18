from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    # 캘린더
    path('', views.calendar_view, name='calendar'),
    path('api/events/', views.calendar_api, name='calendar_api'),
    
    # 이벤트 CRUD
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # 휴원 관리
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/create/', views.holiday_create, name='holiday_create'),
    path('holidays/<int:pk>/update/', views.holiday_update, name='holiday_update'),
    path('holidays/<int:pk>/delete/', views.holiday_delete, name='holiday_delete'),
    
    # 보강 관리
    path('makeups/', views.makeup_list, name='makeup_list'),
    path('makeups/create/', views.makeup_create, name='makeup_create'),
]
