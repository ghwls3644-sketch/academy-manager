from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='index'),
    path('api/events/', views.timetable_api, name='api'),
]
