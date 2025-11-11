from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='all_products'),                        # /products/
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('<str:category>/', views.product_list, name='product_list_by_category')  # /products/electronics/
]
