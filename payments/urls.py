from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('create/', views.payment_create, name='create'),
    path('unpaid/', views.unpaid_list, name='unpaid'),
    path('<int:pk>/edit/', views.payment_update, name='update'),
    path('<int:pk>/delete/', views.payment_delete, name='delete'),
]
