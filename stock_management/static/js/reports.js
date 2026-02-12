// ========== STOCK MANAGEMENT SYSTEM - REPORTS JS ==========
// Version: 1.0
// Functions: Export to Excel, PDF, Print, Copy, WhatsApp

// ========== 1. EXPORT TO EXCEL ==========
function exportToExcel() {
    try {
        const table = document.getElementById('stockTable');
        if (!table) {
            alert('Hakuna data ya kuexport!');
            return;
        }
        
        // Show loading
        const btn = event?.target;
        if (btn) {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Inaandaa...';
            btn.disabled = true;
        }
        
        let csv = [];
        let headers = [];
        
        // Get headers
        table.querySelectorAll('thead th').forEach(th => {
            headers.push(th.textContent.trim());
        });
        csv.push(headers.join(','));
        
        // Get data rows
        let rowCount = 0;
        table.querySelectorAll('tbody tr').forEach(row => {
            if (row.style.display !== 'none') {
                let rowData = [];
                row.querySelectorAll('td').forEach((td, index) => {
                    if (index < headers.length) {
                        let text = td.textContent.trim();
                        text = text.replace(/,/g, ';');
                        text = text.replace(/\n/g, ' ');
                        text = text.replace(/\s+/g, ' ');
                        rowData.push(`"${text}"`);
                    }
                });
                csv.push(rowData.join(','));
                rowCount++;
            }
        });
        
        if (rowCount === 0) {
            alert('Hakuna data ya kuexport!');
            return;
        }
        
        // Add summary
        csv.push('');
        csv.push('"RIPOTI YA STOCK"');
        csv.push(`"Tarehe: ${new Date().toLocaleDateString('sw-TZ')}"`);
        csv.push(`"Jumla: ${rowCount} bidhaa"`);
        
        // Download file
        const csvContent = csv.join('\n');
        const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ripoti_stock_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        // Restore button
        if (btn) {
            btn.innerHTML = '<i class="fas fa-file-excel"></i> Excel';
            btn.disabled = false;
        }
        
        alert(`✓ Ripoti imepakuliwa! (Bidhaa: ${rowCount})`);
        
    } catch (error) {
        console.error('Excel error:', error);
        alert('✗ Kuna tatizo la kupakua faili. Jaribu tena.');
    }
}

// ========== 2. PRINT REPORT ==========
function printReport() {
    try {
        // Hide UI elements
        const sidebar = document.querySelector('.sidebar');
        const navbar = document.querySelector('.navbar');
        const footer = document.querySelector('.footer');
        const buttons = document.querySelectorAll('.btn');
        const pageActions = document.querySelector('.page-actions');
        const btnGroup = document.querySelector('.btn-group');
        
        if (sidebar) sidebar.style.display = 'none';
        if (navbar) navbar.style.display = 'none';
        if (footer) footer.style.display = 'none';
        if (pageActions) pageActions.style.display = 'none';
        if (btnGroup) btnGroup.style.display = 'none';
        
        buttons.forEach(btn => {
            if (!btn.classList.contains('badge')) {
                btn.style.display = 'none';
            }
        });
        
        // Print
        window.print();
        
        // Restore UI
        setTimeout(() => {
            if (sidebar) sidebar.style.display = '';
            if (navbar) navbar.style.display = '';
            if (footer) footer.style.display = '';
            if (pageActions) pageActions.style.display = '';
            if (btnGroup) btnGroup.style.display = '';
            buttons.forEach(btn => {
                btn.style.display = '';
            });
        }, 1000);
        
    } catch (error) {
        console.error('Print error:', error);
        window.print();
    }
}

// ========== 3. EXPORT TO PDF (Print to PDF) ==========
function exportToPDF() {
    printReport();
}

// ========== 4. COPY TO CLIPBOARD ==========
function copyToClipboard() {
    try {
        const table = document.getElementById('stockTable');
        if (!table) {
            alert('Hakuna data ya kunakili!');
            return;
        }
        
        let text = '';
        
        // Headers
        table.querySelectorAll('thead th').forEach(th => {
            text += th.textContent.trim() + '\t';
        });
        text += '\n';
        
        // Data
        let rowCount = 0;
        table.querySelectorAll('tbody tr').forEach(row => {
            if (row.style.display !== 'none') {
                row.querySelectorAll('td').forEach(td => {
                    text += td.textContent.trim() + '\t';
                });
                text += '\n';
                rowCount++;
            }
        });
        
        // Copy to clipboard
        navigator.clipboard.writeText(text).then(() => {
            alert(`✓ Data imenakiliwa! (Bidhaa: ${rowCount})`);
        }).catch(() => {
            alert('✗ Kuna tatizo la kunakili data.');
        });
        
    } catch (error) {
        console.error('Copy error:', error);
        alert('✗ Kuna tatizo la kunakili data.');
    }
}

// ========== 5. WHATSAPP SHARE ==========
function shareWhatsApp() {
    try {
        const count = document.querySelectorAll('#stockTable tbody tr').length;
        const date = new Date().toLocaleDateString('sw-TZ');
        const time = new Date().toLocaleTimeString('sw-TZ');
        
        const text = encodeURIComponent(
            `📊 *RIPOTI YA STOCK*\n` +
            `📅 Tarehe: ${date}\n` +
            `⏰ Saa: ${time}\n` +
            `📦 Bidhaa: ${count}\n` +
            `🏢 Stock Management System`
        );
        
        window.open(`https://wa.me/?text=${text}`, '_blank');
        
    } catch (error) {
        console.error('WhatsApp error:', error);
        alert('✗ Kuna tatizo la kushare kwenye WhatsApp.');
    }
}

// ========== 6. INITIALIZE BUTTONS ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Reports JS initialized');
    
    // Excel button
    const excelBtn = document.querySelector('.btn-success');
    if (excelBtn && excelBtn.textContent.includes('Excel')) {
        excelBtn.onclick = exportToExcel;
        console.log('  ✅ Excel button ready');
    }
    
    // Print button
    const printBtn = document.querySelector('.btn-primary');
    if (printBtn && printBtn.textContent.includes('Print')) {
        printBtn.onclick = printReport;
        console.log('  ✅ Print button ready');
    }
    
    // PDF button
    const pdfBtn = Array.from(document.querySelectorAll('.btn-danger')).find(
        btn => btn.textContent.includes('PDF')
    );
    if (pdfBtn) {
        pdfBtn.onclick = exportToPDF;
        console.log('  ✅ PDF button ready');
    }
    
    // Copy button
    const copyBtn = Array.from(document.querySelectorAll('.btn-info')).find(
        btn => btn.textContent.includes('Nakili') || btn.textContent.includes('Copy')
    );
    if (copyBtn) {
        copyBtn.onclick = copyToClipboard;
        console.log('  ✅ Copy button ready');
    }
    
    // WhatsApp button
    const waBtn = Array.from(document.querySelectorAll('.btn-success')).find(
        btn => btn.textContent.includes('WhatsApp')
    );
    if (waBtn) {
        waBtn.onclick = shareWhatsApp;
        console.log('  ✅ WhatsApp button ready');
    }
});