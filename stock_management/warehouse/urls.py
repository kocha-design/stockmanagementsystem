from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('stockin/', views.add_stockin, name='add_stockin'),
    path('stockout/', views.add_stockout, name='add_stockout'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    
    # API Endpoints
    path('api/product-stock/<int:product_id>/', views.product_stock_api, name='product_stock_api'),
    
    # ===== REPORTS =====
    path('reports/stock/', views.stock_report, name='stock_report'),
    path('reports/transactions/', views.transaction_list, name='transaction_report'),  # <-- REKEBISHA HII!
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    
        path('warehouse/<int:warehouse_id>/', views.warehouse_stock, name='warehouse_stock'),
    path('transfer/', views.transfer_stock, name='transfer_stock'),
]