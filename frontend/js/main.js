document.addEventListener('DOMContentLoaded', function() {
    // Load all components
    loadComponent('header-container', 'components/header.html');
    loadComponent('nav-container', 'components/nav.html');
    loadComponent('footer-container', 'components/footer.html');
    loadComponent('modal-container', 'components/modal.html');

    // Initialize after components are loaded
    setTimeout(() => {
        Modal.init();
        Auth.init();
    }, 1000);
});

// Function to load components
async function loadComponent(containerId, componentPath) {
    try {
        const response = await fetch(componentPath);
        const data = await response.text();
        document.getElementById(containerId).innerHTML = data;
    } catch (error) {
        console.error(`Error loading component ${componentPath}:`, error);
    }
}

// Utility function for showing toast messages
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }, 100);
}
