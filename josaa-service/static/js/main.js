// Main JavaScript for JOSAA College Preference Generator

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFormHandling();
    setupTableSorting();
    setupFilteringAndSearch();
    setupCollegeTypeToggle();
    setupProbabilitySlider();
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
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Prediction failed');
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

                showToast('Preferences generated successfully', 'success');
            } catch (error) {
                console.error('Prediction error:', error);
                showToast('Failed to generate preferences. Please try again.', 'error');
            } finally {
                hideLoading();
            }
        });
    }
}

// Form Validation
function validateForm(form) {
    const rank = form.querySelector('#jee_rank').value;
    const category = form.querySelector('#category').value;
    const collegeType = form.querySelector('#college_type').value;
    const round = form.querySelector('#round_no').value;

    if (!rank || rank < 1) {
        showToast('Please enter a valid JEE rank', 'error');
        return false;
    }

    if (!category) {
        showToast('Please select a category', 'error');
        return false;
    }

    if (!collegeType) {
        showToast('Please select a college type', 'error');
        return false;
    }

    if (!round) {
        showToast('Please select a round', 'error');
        return false;
    }

    return true;
}

// College Type Toggle
function setupCollegeTypeToggle() {
    const collegeTypeSelect = document.getElementById('college_type');
    const rankLabel = document.querySelector('label[for="jee_rank"]');

    if (collegeTypeSelect && rankLabel) {
        collegeTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            if (selectedType === 'IIT') {
                rankLabel.textContent = 'Your JEE Advanced Rank';
            } else {
                rankLabel.textContent = 'Your JEE Main Rank';
            }
        });
    }
}

// Probability Slider
function setupProbabilitySlider() {
    const slider = document.getElementById('min_probability');
    const sliderValue = document.getElementById('probability_value');

    if (slider && sliderValue) {
        slider.addEventListener('input', function() {
            sliderValue.textContent = this.value + '%';
        });
    }
}

// Table Sorting
function setupTableSorting() {
    const table = document.querySelector('.results-table');
    if (table) {
        const headers = table.querySelectorAll('th[data-sortable="true"]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.dataset.column;
                const isNumeric = header.dataset.type === 'number';
                sortTable(table, column, isNumeric);
            });
        });
    }
}

function sortTable(table, column, isNumeric) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const currentDir = table.dataset.sortDir === 'asc' ? 'desc' : 'asc';
    table.dataset.sortDir = currentDir;

    const sortedRows = rows.sort((a, b) => {
        let aVal = a.querySelector(`td[data-column="${column}"]`).textContent;
        let bVal = b.querySelector(`td[data-column="${column}"]`).textContent;

        if (isNumeric) {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        }

        if (currentDir === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    tbody.innerHTML = '';
    sortedRows.forEach(row => tbody.appendChild(row));

    // Update sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    const header = table.querySelector(`th[data-column="${column}"]`);
    header.classList.add(`sort-${currentDir}`);
}

// Filtering and Search
function setupFilteringAndSearch() {
    const searchInput = document.getElementById('college_search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterTable(this.value);
        }, 300));
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

// Responsive Handling
function setupResponsiveHandling() {
    const table = document.querySelector('.results-table');
    if (table) {
        makeTableResponsive(table);
    }
}

function makeTableResponsive(table) {
    if (window.innerWidth < 768) {
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
        table.querySelectorAll('tbody tr').forEach(row => {
            row.querySelectorAll('td').forEach((cell, index) => {
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
    toast.className = `toast toast-${type}`;
    
    // Add icon based on type
    const icon = document.createElement('i');
    icon.className = `fas fa-${
        type === 'success' ? 'check-circle' : 
        type === 'error' ? 'exclamation-circle' : 
        'info-circle'
    }`;
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

// Export functionality
function exportToCSV() {
    const table = document.querySelector('.results-table');
    if (!table) return;

    const rows = table.querySelectorAll('tr');
    const csvContent = [];

    rows.forEach(row => {
        const rowData = [];
        row.querySelectorAll('th, td').forEach(cell => {
            rowData.push(`"${cell.textContent.replace(/"/g, '""')}"`);
        });
        csvContent.push(rowData.join(','));
    });

    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'josaa_preferences.csv';
    link.click();
    URL.revokeObjectURL(link.href);
}

// Handle back/forward browser navigation
window.addEventListener('popstate', function() {
    location.reload();
});

// Window resize handling
window.addEventListener('resize', debounce(() => {
    const table = document.querySelector('.results-table');
    if (table) {
        makeTableResponsive(table);
    }
}, 250));
