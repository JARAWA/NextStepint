// Auth handling
let currentAuthForm = 'login';

function showAuthModal() {
    const modal = document.getElementById('authModal');
    modal.style.display = 'block';
    toggleAuthForm(currentAuthForm);
}

function hideAuthModal() {
    const modal = document.getElementById('authModal');
    modal.style.display = 'none';
}

function toggleAuthForm(formType) {
    currentAuthForm = formType;
    document.getElementById('loginForm').style.display = formType === 'login' ? 'block' : 'none';
    document.getElementById('registerForm').style.display = formType === 'register' ? 'block' : 'none';
}

// Form submissions
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }
        
        location.reload();
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed', 'error');
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Registration failed');
        }
        
        location.reload();
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed', 'error');
    }
});

async function handleLogout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Logout failed');
        }
        
        location.reload();
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Logout failed', 'error');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        hideAuthModal();
    }
}

// Close button
document.querySelector('.modal .close').onclick = hideAuthModal;
