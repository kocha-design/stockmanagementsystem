from django.contrib import admin
from .models import Category, Product, Warehouse, StockIn, StockOut

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'unit_price', 'reorder_level']
    list_filter = ['category']
    search_fields = ['name', 'sku']

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'manager']
    search_fields = ['name', 'location']

@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'supplier', 'date_received', 'warehouse']
    list_filter = ['date_received', 'warehouse']
    search_fields = ['product__name', 'supplier', 'reference_no']

@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'customer', 'date_issued', 'warehouse']
    list_filter = ['date_issued', 'warehouse']
    search_fields = ['product__name', 'customer', 'reference_no']