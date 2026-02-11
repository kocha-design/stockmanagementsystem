// Main JavaScript for Stock Management System
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-update current date/time in forms
    const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    if (dateInputs.length > 0) {
        const now = new Date();
        const localDateTime = now.toISOString().slice(0, 16);
        
        dateInputs.forEach(input => {
            if (!input.value) {
                input.value = localDateTime;
            }
        });
    }
    
    // Stock level warnings
    const stockLevelElements = document.querySelectorAll('.stock-level');
    stockLevelElements.forEach(element => {
        const stock = parseInt(element.textContent);
        if (stock <= 0) {
            element.classList.add('text-danger', 'fw-bold');
            element.innerHTML = '<i class="fas fa-times-circle"></i> ' + stock;
        } else if (stock <= 10) {
            element.classList.add('text-warning', 'fw-bold');
            element.innerHTML = '<i class="fas fa-exclamation-triangle"></i> ' + stock;
        } else {
            element.classList.add('text-success');
        }
    });
    
    // Search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });
    
    // Confirm before deleting
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Je, una uhakika unataka kufuta hii rekodi?')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-refresh dashboard every 30 seconds
    if (window.location.pathname === '/') {
        setInterval(() => {
            const notifications = document.querySelectorAll('.alert');
            if (notifications.length === 0) {
                window.location.reload();
            }
        }, 30000);
    }
    
    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });
    
    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Add to existing main.js
document.addEventListener('DOMContentLoaded', function() {
    
    // Stock availability check for stockout form
    const productSelect = document.getElementById('id_product');
    const quantityInput = document.getElementById('id_quantity');
    
    if (productSelect && quantityInput) {
        productSelect.addEventListener('change', function() {
            const productId = this.value;
            if (productId) {
                fetch(`/api/product-stock/${productId}/`)
                    .then(response => response.json())
                    .then(data => {
                        const stockInfo = document.getElementById('stock-info');
                        if (!stockInfo) {
                            const div = document.createElement('div');
                            div.id = 'stock-info';
                            div.className = 'alert alert-info mt-2';
                            quantityInput.parentNode.appendChild(div);
                        }
                        
                        const stockElement = document.getElementById('stock-info');
                        stockElement.innerHTML = `
                            <i class="fas fa-box"></i> Stock inayopatikana: <strong>${data.stock}</strong>
                            ${data.status === 'low' ? '<span class="badge bg-warning ms-2">Stock Ndogo</span>' : ''}
                            ${data.status === 'out' ? '<span class="badge bg-danger ms-2">Hakuna Stock</span>' : ''}
                        `;
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            }
        });
    }
    
    // Auto-generate reference numbers
    const refNoInput = document.getElementById('id_reference_no');
    if (refNoInput && !refNoInput.value) {
        const now = new Date();
        const dateStr = now.toISOString().slice(0,10).replace(/-/g, '');
        const randomNum = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        refNoInput.value = `REF-${dateStr}-${randomNum}`;
    }
});