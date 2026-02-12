from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Product, Warehouse, StockIn, StockOut, Category  # <-- HII IKO SAHIHI!
from .forms import StockInForm, StockOutForm

# ========== DASHBOARD ==========
@login_required(login_url='/admin/login/')
def dashboard(request):
    """Dashboard homepage"""
    try:
        today = timezone.now().date()
        
        # Basic counts
        total_products = Product.objects.count()
        total_categories = Category.objects.count()  # <-- HII INAPIGA CALL KWENYE MODELS!
        total_warehouses = Warehouse.objects.count()
        
        # Today's transactions
        today_stockins = StockIn.objects.filter(
            date_received__date=today
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        today_stockouts = StockOut.objects.filter(
            date_issued__date=today
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Low stock products
        low_stock_products = []
        for product in Product.objects.all():
            total_stock = product.get_total_stock()
            
            if total_stock <= product.reorder_level:
                low_stock_products.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'current_stock': total_stock,
                    'reorder_level': product.reorder_level,
                    'category': product.category.name if product.category else '-'
                })
        
        # Recent transactions
        recent_stockins = StockIn.objects.select_related('product', 'warehouse').order_by('-date_received')[:5]
        recent_stockouts = StockOut.objects.select_related('product', 'warehouse').order_by('-date_issued')[:5]
        
        context = {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_warehouses': total_warehouses,
            'today_stockins': today_stockins,
            'today_stockouts': today_stockouts,
            'low_stock_products': low_stock_products[:10],
            'recent_stockins': recent_stockins,
            'recent_stockouts': recent_stockouts,
            'today': today.strftime('%d %B %Y'),
        }
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        context = {
            'total_products': 0,
            'total_categories': 0,
            'total_warehouses': 0,
            'today_stockins': 0,
            'today_stockouts': 0,
            'low_stock_products': [],
            'recent_stockins': [],
            'recent_stockouts': [],
            'today': timezone.now().date().strftime('%d %B %Y'),
        }
    
    return render(request, 'warehouse/dashboard.html', context)


# ========== PRODUCTS ==========
@login_required(login_url='/admin/login/')
def product_list(request):
    """List all products"""
    try:
        products = Product.objects.select_related('category').all()
        
        # Add stock info to each product
        for product in products:
            product.total_stock = product.get_total_stock()
        
        context = {
            'products': products,
        }
        
    except Exception as e:
        print(f"Product list error: {e}")
        context = {
            'products': [],
        }
    
    return render(request, 'warehouse/products/list.html', context)


@login_required(login_url='/admin/login/')
def product_detail(request, pk):
    """Product details with warehouse breakdown"""
    try:
        product = get_object_or_404(Product, pk=pk)
        warehouses = Warehouse.objects.all()
        
        # Stock by warehouse
        stock_by_warehouse = []
        for warehouse in warehouses:
            stock = product.get_stock_by_warehouse(warehouse)
            stock_by_warehouse.append({
                'warehouse': warehouse,
                'stock': stock,
                'status': 'out' if stock <= 0 else 'low' if stock <= product.reorder_level else 'ok'
            })
        
        # Transaction history
        stockins = StockIn.objects.filter(product=product).select_related('warehouse').order_by('-date_received')[:20]
        stockouts = StockOut.objects.filter(product=product).select_related('warehouse').order_by('-date_issued')[:20]
        
        context = {
            'product': product,
            'stock_by_warehouse': stock_by_warehouse,
            'total_stock': product.get_total_stock(),
            'stockins': stockins,
            'stockouts': stockouts,
            'warehouses': warehouses,
        }
        
    except Exception as e:
        print(f"Product detail error: {e}")
        context = {
            'product': None,
            'stock_by_warehouse': [],
            'total_stock': 0,
            'stockins': [],
            'stockouts': [],
            'warehouses': [],
        }
    
    return render(request, 'warehouse/products/detail.html', context)


# ========== STOCK TRANSACTIONS ==========
@login_required(login_url='/admin/login/')
def add_stockin(request):
    """Add stock in transaction"""
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            try:
                stockin = form.save(commit=False)
                stockin.received_by = request.user
                stockin.save()
                messages.success(request, f'✓ Stock ya {stockin.product.name} imeingizwa kikamilifu kwenye {stockin.warehouse.name}!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'✗ Kuna tatizo: {str(e)}')
    else:
        form = StockInForm()
    
    context = {
        'form': form,
        'warehouses': Warehouse.objects.all(),
        'products': Product.objects.all(),
    }
    return render(request, 'warehouse/transactions/stockin_form.html', context)


@login_required(login_url='/admin/login/')
def add_stockout(request):
    """Add stock out transaction"""
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            try:
                stockout = form.save(commit=False)
                stockout.issued_by = request.user
                
                # Check stock availability
                current_stock = stockout.product.get_stock_by_warehouse(stockout.warehouse)
                if stockout.quantity > current_stock:
                    messages.error(request, f'✗ Stock haitoshi kwenye {stockout.warehouse.name}! Iliyopo: {current_stock}')
                else:
                    stockout.save()
                    messages.success(request, f'✓ Stock ya {stockout.product.name} imetolewa kikamilifu kutoka {stockout.warehouse.name}!')
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'✗ Kuna tatizo: {str(e)}')
    else:
        form = StockOutForm()
    
    context = {
        'form': form,
        'warehouses': Warehouse.objects.all(),
        'products': Product.objects.all(),
    }
    return render(request, 'warehouse/transactions/stockout_form.html', context)


@login_required(login_url='/admin/login/')
def transaction_list(request):
    """List all transactions"""
    try:
        stockins = StockIn.objects.select_related('product', 'warehouse').order_by('-date_received')[:100]
        stockouts = StockOut.objects.select_related('product', 'warehouse').order_by('-date_issued')[:100]
        
        # Calculate totals
        stockins_total = sum(s.quantity for s in stockins)
        stockouts_total = sum(s.quantity for s in stockouts)
        
        context = {
            'stockins': stockins,
            'stockouts': stockouts,
            'stockins_total': stockins_total,
            'stockouts_total': stockouts_total,
            'total_transactions': stockins.count() + stockouts.count(),
        }
        
    except Exception as e:
        print(f"Transaction list error: {e}")
        context = {
            'stockins': [],
            'stockouts': [],
            'stockins_total': 0,
            'stockouts_total': 0,
            'total_transactions': 0,
        }
    
    return render(request, 'warehouse/transactions/list.html', context)


# ========== WAREHOUSE MANAGEMENT ==========
@login_required(login_url='/admin/login/')
def warehouse_stock(request, warehouse_id):
    """View stock in specific warehouse"""
    try:
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        products = Product.objects.all()
        
        product_data = []
        total_items = 0
        total_value = 0
        
        for product in products:
            stock = product.get_stock_by_warehouse(warehouse)
            value = stock * product.unit_price
            total_items += stock
            total_value += value
            
            product_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else '-',
                'unit_price': product.unit_price,
                'stock': stock,
                'value': value,
                'reorder_level': product.reorder_level,
                'status': 'out' if stock <= 0 else 'low' if stock <= product.reorder_level else 'ok'
            })
        
        context = {
            'warehouse': warehouse,
            'products': product_data,
            'total_products': len(product_data),
            'total_items': total_items,
            'total_value': total_value,
        }
        
    except Exception as e:
        print(f"Warehouse stock error: {e}")
        context = {
            'warehouse': None,
            'products': [],
            'total_products': 0,
            'total_items': 0,
            'total_value': 0,
        }
    
    return render(request, 'warehouse/warehouse_stock.html', context)


@login_required(login_url='/admin/login/')
def transfer_stock(request):
    """Transfer stock between warehouses"""
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product')
            from_warehouse_id = request.POST.get('from_warehouse')
            to_warehouse_id = request.POST.get('to_warehouse')
            quantity = int(request.POST.get('quantity', 0))
            
            product = get_object_or_404(Product, id=product_id)
            from_warehouse = get_object_or_404(Warehouse, id=from_warehouse_id)
            to_warehouse = get_object_or_404(Warehouse, id=to_warehouse_id)
            
            # Check stock availability
            current_stock = product.get_stock_by_warehouse(from_warehouse)
            
            if quantity > current_stock:
                messages.error(request, f'✗ Hakuna stock ya kutosha kwenye {from_warehouse.name}! Iliyopo: {current_stock}')
            elif from_warehouse == to_warehouse:
                messages.error(request, '✗ Maghala yanayotumika ni tofauti!')
            else:
                # Create StockOut from source warehouse
                StockOut.objects.create(
                    product=product,
                    warehouse=from_warehouse,
                    quantity=quantity,
                    customer=f'Transfer to {to_warehouse.name}',
                    reference_no=f'TRF-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    issued_by=request.user,
                    notes=f'Stock transfer from {from_warehouse.name} to {to_warehouse.name}'
                )
                
                # Create StockIn to destination warehouse
                StockIn.objects.create(
                    product=product,
                    warehouse=to_warehouse,
                    quantity=quantity,
                    supplier=f'Transfer from {from_warehouse.name}',
                    reference_no=f'TRF-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    received_by=request.user,
                    notes=f'Stock transfer from {from_warehouse.name} to {to_warehouse.name}'
                )
                
                messages.success(request, f'✓ Stock imehamishwa kutoka {from_warehouse.name} hadi {to_warehouse.name}!')
                return redirect('warehouse_stock', warehouse_id=from_warehouse.id)
                
        except Exception as e:
            messages.error(request, f'✗ Kuna tatizo: {str(e)}')
    
    # GET request - show form
    warehouses = Warehouse.objects.all()
    products = Product.objects.all()
    
    context = {
        'warehouses': warehouses,
        'products': products,
    }
    return render(request, 'warehouse/transfer_stock.html', context)


# ========== REPORTS ==========
@login_required(login_url='/admin/login/')
def stock_report(request):
    """Generate stock report"""
    try:
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        product_data = []
        total_items = 0
        total_value = 0
        low_stock_count = 0
        out_of_stock_count = 0
        
        for product in products:
            current_stock = product.get_total_stock()
            value = current_stock * product.unit_price
            
            total_items += current_stock
            total_value += value
            
            if current_stock <= 0:
                out_of_stock_count += 1
            elif current_stock <= product.reorder_level:
                low_stock_count += 1
            
            # Get stock by warehouse
            stock_by_warehouse = {}
            for warehouse in warehouses:
                stock_by_warehouse[warehouse.id] = product.get_stock_by_warehouse(warehouse)
            
            product_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category.name if product.category else '-',
                'unit_price': product.unit_price,
                'current_stock': current_stock,
                'total_value': value,
                'reorder_level': product.reorder_level,
                'stock_by_warehouse': stock_by_warehouse,
            })
        
        # Warehouse summary
        warehouse_data = []
        for warehouse in warehouses:
            wh_total = 0
            wh_value = 0
            for product in products:
                stock = product.get_stock_by_warehouse(warehouse)
                wh_total += stock
                wh_value += stock * product.unit_price
            warehouse_data.append({
                'id': warehouse.id,
                'name': warehouse.name,
                'code': warehouse.code,
                'total_items': wh_total,
                'total_value': wh_value,
            })
        
        context = {
            'products': product_data,
            'warehouses': warehouse_data,
            'report_date': timezone.now(),
            'total_items': total_items,
            'total_value': total_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'in_stock_count': products.count() - low_stock_count - out_of_stock_count,
            'has_data': products.count() > 0,
        }
        
    except Exception as e:
        print(f"Stock report error: {e}")
        context = {
            'products': [],
            'warehouses': [],
            'report_date': timezone.now(),
            'total_items': 0,
            'total_value': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'in_stock_count': 0,
            'has_data': False,
        }
    
    return render(request, 'warehouse/reports/stock_report.html', context)


@login_required(login_url='/admin/login/')
def low_stock_report(request):
    """Generate low stock report"""
    try:
        products = Product.objects.all()
        low_stock_products = []
        
        for product in products:
            current_stock = product.get_total_stock()
            reorder_level = product.reorder_level
            
            if current_stock <= reorder_level:
                needed_quantity = (reorder_level * 2) - current_stock if current_stock > 0 else reorder_level * 2
                
                low_stock_products.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'category': product.category.name if product.category else '-',
                    'current_stock': current_stock,
                    'reorder_level': reorder_level,
                    'unit_price': product.unit_price,
                    'total_value': current_stock * product.unit_price,
                    'needed_quantity': needed_quantity,
                    'order_value': needed_quantity * product.unit_price,
                    'status': 'out' if current_stock <= 0 else 'low'
                })
        
        context = {
            'products': low_stock_products,
            'report_date': timezone.now(),
            'total_low_stock': len(low_stock_products),
            'has_data': len(low_stock_products) > 0,
        }
        
    except Exception as e:
        print(f"Low stock report error: {e}")
        context = {
            'products': [],
            'report_date': timezone.now(),
            'total_low_stock': 0,
            'has_data': False,
        }
    
    return render(request, 'warehouse/reports/low_stock_report.html', context)


@login_required(login_url='/admin/login/')
def transaction_report(request):
    """Generate transaction report"""
    try:
        stockins = StockIn.objects.select_related('product', 'warehouse').order_by('-date_received')[:100]
        stockouts = StockOut.objects.select_related('product', 'warehouse').order_by('-date_issued')[:100]
        
        stockins_total = sum(s.quantity for s in stockins)
        stockouts_total = sum(s.quantity for s in stockouts)
        
        context = {
            'stockins': stockins,
            'stockouts': stockouts,
            'stockins_total': stockins_total,
            'stockouts_total': stockouts_total,
            'total_transactions': stockins.count() + stockouts.count(),
            'report_date': timezone.now(),
            'has_data': stockins.exists() or stockouts.exists(),
        }
        
    except Exception as e:
        print(f"Transaction report error: {e}")
        context = {
            'stockins': [],
            'stockouts': [],
            'stockins_total': 0,
            'stockouts_total': 0,
            'total_transactions': 0,
            'report_date': timezone.now(),
            'has_data': False,
        }
    
    return render(request, 'warehouse/reports/transaction_report.html', context)


@login_required(login_url='/admin/login/')
def monthly_report(request):
    """Generate monthly report"""
    try:
        today = timezone.now().date()
        first_day = today.replace(day=1)
        
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1)
        
        # Monthly transactions
        monthly_stockins = StockIn.objects.filter(
            date_received__date__gte=first_day,
            date_received__date__lt=last_day
        ).select_related('product', 'warehouse')
        
        monthly_stockouts = StockOut.objects.filter(
            date_issued__date__gte=first_day,
            date_issued__date__lt=last_day
        ).select_related('product', 'warehouse')
        
        # Calculate totals
        monthly_in_total = monthly_stockins.aggregate(total=Sum('quantity'))['total'] or 0
        monthly_out_total = monthly_stockouts.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Top products
        products = Product.objects.all()
        top_products = []
        
        for product in products:
            monthly_in = monthly_stockins.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
            monthly_out = monthly_stockouts.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
            
            if monthly_in > 0 or monthly_out > 0:
                top_products.append({
                    'name': product.name,
                    'sku': product.sku,
                    'monthly_in': monthly_in,
                    'monthly_out': monthly_out,
                    'total': monthly_in + monthly_out
                })
        
        # Sort by total activity
        top_products.sort(key=lambda x: x['total'], reverse=True)
        
        context = {
            'month': today.strftime('%B %Y'),
            'year': today.year,
            'month_name': today.strftime('%B'),
            'monthly_stockins': monthly_stockins[:50],
            'monthly_stockouts': monthly_stockouts[:50],
            'monthly_in_total': monthly_in_total,
            'monthly_out_total': monthly_out_total,
            'total_transactions': monthly_stockins.count() + monthly_stockouts.count(),
            'top_products': top_products[:10],
            'report_date': timezone.now(),
            'has_data': monthly_stockins.exists() or monthly_stockouts.exists(),
        }
        
    except Exception as e:
        print(f"Monthly report error: {e}")
        context = {
            'month': timezone.now().strftime('%B %Y'),
            'year': timezone.now().year,
            'month_name': timezone.now().strftime('%B'),
            'monthly_stockins': [],
            'monthly_stockouts': [],
            'monthly_in_total': 0,
            'monthly_out_total': 0,
            'total_transactions': 0,
            'top_products': [],
            'report_date': timezone.now(),
            'has_data': False,
        }
    
    return render(request, 'warehouse/reports/monthly_report.html', context)


# ========== API ENDPOINTS ==========
@login_required(login_url='/admin/login/')
def product_stock_api(request, product_id):
    """API to get product stock info for specific warehouse"""
    try:
        product = get_object_or_404(Product, id=product_id)
        warehouse_id = request.GET.get('warehouse')
        
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            current_stock = product.get_stock_by_warehouse(warehouse)
            warehouse_name = warehouse.name
        else:
            current_stock = product.get_total_stock()
            warehouse_name = 'All Warehouses'
        
        if current_stock <= 0:
            status = 'out'
            status_text = 'Hakuna Stock'
        elif current_stock <= product.reorder_level:
            status = 'low'
            status_text = 'Stock Ndogo'
        else:
            status = 'ok'
            status_text = 'Ipo'
        
        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'sku': product.sku,
            'warehouse': warehouse_name,
            'stock': current_stock,
            'status': status,
            'status_text': status_text,
            'reorder_level': product.reorder_level,
            'unit_price': str(product.unit_price),
        })
        
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    