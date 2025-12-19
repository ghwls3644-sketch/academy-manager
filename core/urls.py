from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('api/search/', views.global_search, name='global_search'),
]
