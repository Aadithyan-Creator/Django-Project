from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('create/', views.account_create, name='account_create'),
    path('edit/<int:pk>/', views.account_edit, name='account_edit'),
    path('detail/<int:pk>/', views.account_detail, name='account_detail'),
    path('deactivate/<int:pk>/', views.account_deactivate, name='account_deactivate'),
    path('delete/<int:pk>/', views.account_delete, name='account_delete'),
]
