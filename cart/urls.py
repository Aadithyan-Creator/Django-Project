from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_list, name='cart_list'),
    path('create/', views.cart_create, name='cart_create'),
    path('add-items/', views.cart_add_items, name='cart_add_items'),
    path('checkout/', views.cart_checkout, name='cart_checkout'),
    path('update/<int:pk>/', views.cart_update, name='cart_update'),
    path('delete/<int:pk>/', views.cart_delete, name='cart_delete'),
]
