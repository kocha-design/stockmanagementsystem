from django import forms
from .models import Product, Warehouse, StockIn, StockOut

class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = ['product', 'warehouse', 'quantity', 'supplier', 'reference_no', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active products
        self.fields['product'].queryset = Product.objects.all()
        self.fields['warehouse'].queryset = Warehouse.objects.all()

class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = ['product', 'warehouse', 'quantity', 'customer', 'reference_no', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.all()
        self.fields['warehouse'].queryset = Warehouse.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            # Calculate current stock
            from django.db.models import Sum
            total_in = StockIn.objects.filter(product=product).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            total_out = StockOut.objects.filter(product=product).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            current_stock = total_in - total_out
            
            if quantity > current_stock:
                raise forms.ValidationError(
                    f"Stock haitoshi! Stock iliyopo ni {current_stock}, unajaribu kutoa {quantity}."
                )
        
        return cleaned_data