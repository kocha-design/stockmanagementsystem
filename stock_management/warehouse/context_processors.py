# warehouse/context_processors.py
from .models import Warehouse

def warehouses(request):
    """Add all warehouses to template context"""
    return {
        'warehouses': Warehouse.objects.all().order_by('id', 'name')
    }