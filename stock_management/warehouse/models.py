from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_level = models.IntegerField(default=10)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"

class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=200)
    reference_no = models.CharField(max_length=100, unique=True)
    date_received = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"IN: {self.product.name} - {self.quantity}"

class StockOut(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    customer = models.CharField(max_length=200)
    reference_no = models.CharField(max_length=100, unique=True)
    date_issued = models.DateTimeField(default=timezone.now)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"OUT: {self.product.name} - {self.quantity}"