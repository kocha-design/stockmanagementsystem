from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('stockin/', views.add_stockin, name='add_stockin'),
    path('stockout/', views.add_stockout, name='add_stockout'),
    path('transactions/', views.transaction_list, name='transaction_list'),
]