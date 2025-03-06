class Auth {
    static isLoggedIn = false;
    static user = null;

    static init() {
        // Check if user is already logged in
        const token = localStorage.getItem('token');
        const userData = localStorage.getItem('user');
        
        if (token && userData) {
            this.isLoggedIn = true;
            this.user = JSON.parse(userData);
            this.updateUI();
        }

        this.setupAuthButtons();
    }

    static setupAuthButtons() {
        const generateButtons = document.querySelectorAll('[data-requires-login="true"]');
        generateButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!this.isLoggedIn) {
                    e.preventDefault();
                    Modal.show();
                }
            });
        });
    }

    static async handleLogin(event) {
        event.preventDefault();

        // Clear previous errors
        Modal.hideError('loginEmailError');
        Modal.hideError('loginPasswordError');

        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        try {
            // Get users from localStorage
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            
            // Find user
            const user = users.find(u => u.email === email);

            if (!user || user.password !== btoa(password)) {
                Modal.showError('loginPasswordError', 'Invalid email or password');
                return;
            }

            // Login successful
            this.user = {
                id: user.id,
                name: user.name,
                email: user.email
            };

            this.isLoggedIn = true;

            // Generate a simple token
            const token = btoa(`${user.email}:${Date.now()}`);

            // Store auth data
            if (rememberMe) {
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(this.user));
            } else {
                sessionStorage.setItem('token', token);
                sessionStorage.setItem('user', JSON.stringify(this.user));
            }

            this.updateUI();
            Modal.hide();
            showToast('Login successful!', 'success');

        } catch (error) {
            console.error('Login error:', error);
            showToast('Login failed. Please try again.', 'error');
        }
    }

    static async handleSignup(event) {
        event.preventDefault();

        // Clear previous errors
        Modal.hideError('signupNameError');
        Modal.hideError('signupEmailError');
        Modal.hideError('signupPasswordError');
        Modal.hideError('confirmPasswordError');

        const name = document.getElementById('signupName').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Validation
        if (name.length < 2) {
            Modal.showError('signupNameError', 'Name must be at least 2 characters');
            return;
        }

        if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            Modal.showError('signupEmailError', 'Please enter a valid email');
            return;
        }

        if (password.length < 6) {
            Modal.showError('signupPasswordError', 'Password must be at least 6 characters');
            return;
        }

        if (password !== confirmPassword) {
            Modal.showError('confirmPasswordError', 'Passwords do not match');
            return;
        }

        try {
            // Get existing users
            const users = JSON.parse(localStorage.getItem('users') || '[]');

            // Check if email already exists
            if (users.some(user => user.email === email)) {
                Modal.showError('signupEmailError', 'Email already registered');
                return;
            }

            // Create new user
            const newUser = {
                id: Date.now(),
                name,
                email,
                password: btoa(password) // Basic encryption (not secure for production)
            };

            // Save user
            users.push(newUser);
            localStorage.setItem('users', JSON.stringify(users));

            // Auto login after signup
            this.user = {
                id: newUser.id,
                name: newUser.name,
                email: newUser.email
            };

            this.isLoggedIn = true;
            const token = btoa(`${newUser.email}:${Date.now()}`);
            
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(this.user));

            this.updateUI();
            Modal.hide();
            showToast('Account created successfully!', 'success');

        } catch (error) {
            console.error('Signup error:', error);
            showToast('Signup failed. Please try again.', 'error');
        }
    }

    static logout() {
        this.isLoggedIn = false;
        this.user = null;
        
        // Clear auth data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        
        this.updateUI();
        showToast('Logged out successfully', 'success');
    }

    static updateUI() {
        const generateButtons = document.querySelectorAll('[data-requires-login="true"]');
        const userInfo = document.getElementById('user-info');
        
        if (this.isLoggedIn && this.user) {
            // Update UI for logged-in state
            generateButtons.forEach(btn => {
                if (btn.tagName === 'A') {
                    btn.style.pointerEvents = 'auto';
                }
            });

            if (userInfo) {
                userInfo.innerHTML = `
                    <div class="user-menu">
                        <span>Welcome, ${this.user.name}</span>
                        <button onclick="Auth.logout()" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </button>
                    </div>
                `;
            }
        } else {
            // Update UI for logged-out state
            generateButtons.forEach(btn => {
                if (btn.tagName === 'A') {
                    btn.style.pointerEvents = 'none';
                }
            });

            if (userInfo) {
                userInfo.innerHTML = `
                    <button onclick="Modal.show()" class="login-btn">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </button>
                `;
            }
        }
    }
}

// Add toast functionality
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Initialize Auth when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
});
