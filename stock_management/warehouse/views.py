from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Product, Category, Warehouse, StockIn, StockOut
from .forms import StockInForm, StockOutForm  # <-- ADD THIS IMPORT

@login_required(login_url='/admin/login/')
def dashboard(request):
    """Display dashboard with statistics"""
    try:
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        total_warehouses = Warehouse.objects.count()
        
        # Calculate low stock products
        low_stock_products = []
        for product in Product.objects.all():
            # Calculate current stock
            total_in = StockIn.objects.filter(product=product).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            total_out = StockOut.objects.filter(product=product).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            current_stock = total_in - total_out
            
            # Check if low stock
            reorder_level = getattr(product, 'reorder_level', 10)
            if current_stock <= reorder_level:
                product.current_stock = current_stock
                low_stock_products.append(product)
        
        # Get recent transactions
        recent_stockins = StockIn.objects.all().order_by('-date_received')[:5]
        recent_stockouts = StockOut.objects.all().order_by('-date_issued')[:5]
        
        context = {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_warehouses': total_warehouses,
            'low_stock_products': low_stock_products,
            'recent_stockins': recent_stockins,
            'recent_stockouts': recent_stockouts,
        }
        
    except Exception as e:
        # If there's an error, show empty dashboard
        context = {
            'total_products': 0,
            'total_categories': 0,
            'total_warehouses': 0,
            'low_stock_products': [],
            'recent_stockins': [],
            'recent_stockouts': [],
        }
        messages.warning(request, "Ongeza data kwanza kupitia admin panel")
    
    return render(request, 'warehouse/dashboard.html', context)

@login_required(login_url='/admin/login/')
def product_list(request):
    """Display list of all products"""
    products = Product.objects.all()
    
    # Add current stock to each product
    for product in products:
        total_in = StockIn.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_out = StockOut.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        product.current_stock = total_in - total_out
        product.reorder_level = getattr(product, 'reorder_level', 10)
    
    context = {'products': products}
    return render(request, 'warehouse/products/list.html', context)

@login_required(login_url='/admin/login/')
def product_detail(request, pk):
    """Display details of a specific product"""
    product = get_object_or_404(Product, pk=pk)
    
    # Calculate current stock
    total_in = StockIn.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    total_out = StockOut.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    current_stock = total_in - total_out
    
    # Get transaction history
    stockins = StockIn.objects.filter(product=product).order_by('-date_received')[:10]
    stockouts = StockOut.objects.filter(product=product).order_by('-date_issued')[:10]
    
    context = {
        'product': product,
        'current_stock': current_stock,
        'stockins': stockins,
        'stockouts': stockouts,
    }
    
    return render(request, 'warehouse/products/detail.html', context)

@login_required(login_url='/admin/login/')
def add_stockin(request):
    """Add new stock in transaction"""
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stockin = form.save(commit=False)
            stockin.received_by = request.user
            stockin.save()
            messages.success(request, f'Stock ya {stockin.product.name} imeingizwa kikamilifu!')
            return redirect('dashboard')
    else:
        form = StockInForm()
    
    context = {'form': form}
    return render(request, 'warehouse/transactions/stockin_form.html', context)

@login_required(login_url='/admin/login/')
def add_stockout(request):
    """Add new stock out transaction"""
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            stockout = form.save(commit=False)
            stockout.issued_by = request.user
            stockout.save()
            messages.success(request, f'Stock ya {stockout.product.name} imetolewa kikamilifu!')
            return redirect('dashboard')
    else:
        form = StockOutForm()
    
    context = {'form': form}
    return render(request, 'warehouse/transactions/stockout_form.html', context)

@login_required(login_url='/admin/login/')
def transaction_list(request):
    """Display list of all transactions"""
    stockins = StockIn.objects.all().order_by('-date_received')[:50]
    stockouts = StockOut.objects.all().order_by('-date_issued')[:50]
    
    context = {
        'stockins': stockins,
        'stockouts': stockouts,
    }
    
    return render(request, 'warehouse/transactions/list.html', context)