from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('success/<int:pk>/', views.order_success, name='order_success'),
    path('delete/<int:pk>/', views.order_delete, name="order_delete")

]
