from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

# ========== CATEGORY ==========
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

# ========== WAREHOUSE ==========
class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # <-- IMENGEZWA!
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            count = Warehouse.objects.count() + 1
            self.code = f"WH{count:03d}"
        super().save(*args, **kwargs)

# ========== PRODUCT ==========
class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_level = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)  # <-- IMENGEZWA!
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_stock_by_warehouse(self, warehouse):
        """Get current stock for this product in specific warehouse"""
        total_in = StockIn.objects.filter(
            product=self, 
            warehouse=warehouse
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        total_out = StockOut.objects.filter(
            product=self, 
            warehouse=warehouse
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return total_in - total_out
    
    def get_total_stock(self):
        """Get total stock across all warehouses"""
        total_in = StockIn.objects.filter(product=self).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_out = StockOut.objects.filter(product=self).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return total_in - total_out

# ========== STOCK IN ==========
class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stockins')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stockins')
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=200)
    reference_no = models.CharField(max_length=100, unique=True)
    date_received = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_received']
    
    def __str__(self):
        return f"IN: {self.product.name} - {self.quantity} @ {self.warehouse.name}"

# ========== STOCK OUT ==========
class StockOut(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stockouts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stockouts')
    quantity = models.IntegerField()
    customer = models.CharField(max_length=200)
    reference_no = models.CharField(max_length=100, unique=True)
    date_issued = models.DateTimeField(default=timezone.now)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_issued']
    
    def __str__(self):
        return f"OUT: {self.product.name} - {self.quantity} @ {self.warehouse.name}"
    
    def save(self, *args, **kwargs):
        """Check stock availability before saving"""
        if not self.pk:  # Only for new records
            current_stock = self.product.get_stock_by_warehouse(self.warehouse)
            if self.quantity > current_stock:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Hakuna stock ya kutosha kwenye {self.warehouse.name}!\n"
                    f"Stock iliyopo: {current_stock}, unajaribu kutoa: {self.quantity}"
                )
        super().save(*args, **kwargs)