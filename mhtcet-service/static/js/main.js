// Main JavaScript for MHTCET College Finder

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFormHandling();
    setupTableSorting();
    setupFilteringAndSearch();
    setupExportHandling();
    setupResponsiveHandling();
}

// Form Handling
function setupFormHandling() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!validateForm(this)) {
                return;
            }

            showLoading();
            
            try {
                const formData = new FormData(this);
                const response = await fetch('/search', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Search failed');
                }

                const html = await response.text();
                document.documentElement.innerHTML = html;
                
                // Reinitialize components after HTML update
                initializeApp();
                
                // Scroll to results if they exist
                const results = document.querySelector('.results-section');
                if (results) {
                    results.scrollIntoView({ behavior: 'smooth' });
                }

                showToast('Search completed successfully', 'success');
            } catch (error) {
                console.error('Search error:', error);
                showToast('Failed to perform search. Please try again.', 'error');
            } finally {
                hideLoading();
            }
        });
    }
}

// Form Validation
function validateForm(form) {
    const rank = form.querySelector('#rank').value;
    if (!rank || rank < 1) {
        showToast('Please enter a valid rank', 'error');
        return false;
    }
    return true;
}

// Table Sorting
function setupTableSorting() {
    const sortControls = document.querySelector('#sortControls');
    if (sortControls) {
        const sortFieldSelect = document.getElementById('sortField');
        const sortOrderSelect = document.getElementById('sortOrder');
        
        if (sortFieldSelect && sortOrderSelect) {
            sortFieldSelect.addEventListener('change', sortTable);
            sortOrderSelect.addEventListener('change', sortTable);
        }
        
        // Also setup column header sorting if present
        const table = document.querySelector('.results-table');
        if (table) {
            table.querySelectorAll('th').forEach((th, index) => {
                th.addEventListener('click', () => sortTable(table, index));
            });
        }
    }
}

function sortTable() {
    // This handles the dropdown-based sorting
    const field = document.getElementById('sortField')?.value;
    const order = document.getElementById('sortOrder')?.value;
    
    if (!field || !order) return;
    
    const tbody = document.querySelector('.results-table tbody');
    if (!tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        let aVal, bVal;
        
        switch(field) {
            case 'college_name':
                aVal = a.querySelector('td:nth-child(1) .cell-main').textContent;
                bVal = b.querySelector('td:nth-child(1) .cell-main').textContent;
                break;
            case 'branch_name':
                aVal = a.querySelector('td:nth-child(2) .cell-main').textContent;
                bVal = b.querySelector('td:nth-child(2) .cell-main').textContent;
                break;
            case 'category':
                aVal = a.querySelector('td:nth-child(3) .cell-main').textContent;
                bVal = b.querySelector('td:nth-child(3) .cell-main').textContent;
                break;
            case 'quota_type':
                aVal = a.querySelector('td:nth-child(4) .cell-main').textContent;
                bVal = b.querySelector('td:nth-child(4) .cell-main').textContent;
                break;
            case 'rank':
                aVal = parseInt(a.querySelector('td:nth-child(5) .cell-main').textContent.replace('Rank: ', ''));
                bVal = parseInt(b.querySelector('td:nth-child(5) .cell-main').textContent.replace('Rank: ', ''));
                break;
            case 'percentile':
                aVal = parseFloat(a.querySelector('td:nth-child(5) .cell-sub').textContent.replace('Percentile: ', ''));
                bVal = parseFloat(b.querySelector('td:nth-child(5) .cell-sub').textContent.replace('Percentile: ', ''));
                break;
        }

        if (order === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    // Enable export button after sorting is complete
    const exportButton = document.getElementById('exportExcel');
    if (exportButton) {
        exportButton.disabled = false;
    }
}

// Overloaded sortTable function for column header click sorting
function sortTable(table, column) {
    if (!table || column === undefined) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = column === 5 || column === 6; // Rank and Percentile columns

    // Toggle sort direction
    const currentDir = table.querySelector(`th:nth-child(${column + 1})`).dataset.sort || 'asc';
    const newDir = currentDir === 'asc' ? 'desc' : 'asc';

    // Update sort direction indicator
    table.querySelectorAll('th').forEach(th => {
        th.dataset.sort = '';
        th.classList.remove('sort-asc', 'sort-desc');
    });
    table.querySelector(`th:nth-child(${column + 1})`).dataset.sort = newDir;
    table.querySelector(`th:nth-child(${column + 1})`).classList.add(`sort-${newDir}`);

    // Sort rows
    rows.sort((a, b) => {
        let aVal = a.cells[column].textContent.trim();
        let bVal = b.cells[column].textContent.trim();

        if (isNumeric) {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        }

        if (newDir === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    // Update table
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
    
    // Enable export button after sorting is complete
    const exportButton = document.getElementById('exportExcel');
    if (exportButton) {
        exportButton.disabled = false;
    }
}

// Filtering and Search
function setupFilteringAndSearch() {
    const tableFilter = document.querySelector('#tableFilter');
    if (tableFilter) {
        tableFilter.addEventListener('input', function(e) {
            filterTable(e.target.value);
        });
    }
}

function filterTable(query) {
    const table = document.querySelector('.results-table');
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const lowercaseQuery = query.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(lowercaseQuery) ? '' : 'none';
    });
}

// Export Handling - Enhanced with Excel Export
function setupExportHandling() {
    const exportButton = document.getElementById('exportExcel');
    if (exportButton) {
        exportButton.addEventListener('click', handleDownload);
    }
    
    // For backward compatibility, also handle the CSV export form if it exists
    const exportForm = document.querySelector('.export-form');
    if (exportForm) {
        exportForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Check if we want to use Excel export or fallback to CSV
            if (document.getElementById('exportExcel')) {
                handleDownload();
                return;
            }
            
            // Legacy CSV export code
            showLoading();
            
            try {
                const formData = new FormData(this);
                const response = await fetch('/export', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Export failed');
                }

                // Create and click a temporary download link
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'college_results.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                showToast('Export completed successfully', 'success');
            } catch (error) {
                console.error('Export error:', error);
                showToast('Failed to export results. Please try again.', 'error');
            } finally {
                hideLoading();
            }
        });
    }
}

// Handle the Excel download functionality
function handleDownload() {
    showLoading();
    
    try {
        // Get the current search parameters from the form
        const searchForm = document.querySelector('.search-form');
        const formData = new FormData(searchForm);
        
        // Send request to export endpoint
        fetch('/export-excel', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Export failed');
            }
            return response.blob();
        })
        .then(blob => {
            // Create and click a temporary download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'college_results.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast('Export completed successfully', 'success');
        })
        .catch(error => {
            console.error('Export error:', error);
            showToast('Failed to export results. Please try again.', 'error');
        })
        .finally(() => {
            hideLoading();
        });
    } catch (error) {
        console.error('Export setup error:', error);
        showToast('Failed to prepare export. Please try again.', 'error');
        hideLoading();
    }
}

// Responsive Handling
function setupResponsiveHandling() {
    const table = document.querySelector('.results-table');
    if (table) {
        makeTableResponsive(table);
    }
}

function makeTableResponsive(table) {
    const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
    
    if (window.innerWidth < 768) {
        table.querySelectorAll('tbody tr').forEach(row => {
            Array.from(row.cells).forEach((cell, index) => {
                cell.setAttribute('data-label', headers[index]);
            });
        });
    }
}

// UI State Management - Enhanced loading functions
function setLoadingState(isLoading) {
    const generateBtn = document.querySelector('.search-form button[type="submit"]');
    const downloadBtn = document.getElementById('exportExcel');
    const loadingOverlay = document.getElementById('loading-overlay') || document.querySelector('.loading-overlay');
    
    if (generateBtn) {
        const spinner = generateBtn.querySelector('.spinner-border');
        const buttonContent = generateBtn.querySelector('.button-content');
        
        if (isLoading) {
            generateBtn.disabled = true;
            if (downloadBtn) downloadBtn.disabled = true;
            
            if (loadingOverlay) loadingOverlay.classList.remove('d-none');
            
            if (spinner) spinner.classList.remove('d-none');
            if (buttonContent) buttonContent.classList.add('d-none');
        } else {
            generateBtn.disabled = false;
            if (downloadBtn) downloadBtn.disabled = false;
            
            if (loadingOverlay) loadingOverlay.classList.add('d-none');
            
            if (spinner) spinner.classList.add('d-none');
            if (buttonContent) buttonContent.classList.remove('d-none');
        }
    }
}

// Loading State - Enhanced with UI state management
function showLoading() {
    setLoadingState(true);
    
    // For backward compatibility with the existing code
    document.body.classList.add('loading');
    if (!document.querySelector('.loading-overlay')) {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.id = 'loading-overlay';
        document.body.appendChild(loadingOverlay);
    }
}

function hideLoading() {
    setLoadingState(false);
    
    // For backward compatibility with the existing code
    document.body.classList.remove('loading');
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Add icon based on type
    const icon = document.createElement('i');
    icon.className = `fas fa-${type === 'success' ? 'check-circle' : 
                          type === 'error' ? 'exclamation-circle' : 
                          'info-circle'}`;
    toast.appendChild(icon);

    // Add message
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    toast.appendChild(messageSpan);

    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'toast-close';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = () => toast.remove();
    toast.appendChild(closeButton);

    // Add toast to document
    document.body.appendChild(toast);

    // Remove toast after 5 seconds
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Window resize handling
window.addEventListener('resize', debounce(() => {
    const table = document.querySelector('.results-table');
    if (table) {
        makeTableResponsive(table);
    }
}, 250));

// Handle back/forward browser navigation
window.addEventListener('popstate', function() {
    location.reload();
});
