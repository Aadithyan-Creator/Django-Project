from django.urls import path
from . import views

urlpatterns = [
    # Cart views
    path('', views.cart_list, name='cart_list'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:pk>/', views.cart_update, name='cart_update'),
    path('delete/<int:pk>/', views.cart_delete, name='cart_delete'),
    path('add-item/', views.cart_add_item, name='cart_add_item'),

    # Integrated checkout
    path('checkout/', views.checkout, name='checkout_page'),  # Handles both GET & POST for coupon and place order
     path('place-order/', views.place_order, name='place_order'),

    # Order success/detail page

]
