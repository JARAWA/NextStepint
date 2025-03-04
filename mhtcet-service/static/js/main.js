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
    const table = document.querySelector('.results-table');
    if (table) {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.classList.contains('sortable')) {
                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            }
        });
    }
}

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
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

// Export Handling
function setupExportHandling() {
    const exportForm = document.querySelector('.export-form');
    if (exportForm) {
        exportForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
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

// Loading State
function showLoading() {
    document.body.classList.add('loading');
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    document.body.appendChild(loadingOverlay);
}

function hideLoading() {
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
