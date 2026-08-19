const API_BASE = 'http://192.168.166.20:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('hyperion_token');
    if (token) {
        window.location.href = 'dashboard.php';
    }
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const errBox = document.getElementById('login-error');
    const errText = document.getElementById('error-text');
    const btn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');

    errBox.classList.add('hidden');
    btn.disabled = true;
    btn.classList.add('opacity-80', 'cursor-not-allowed');
    btnText.innerText = 'Authenticating...';
    btnSpinner.classList.remove('hidden');

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('hyperion_token', data.access_token);
            window.location.href = 'dashboard.php';
        } else {
            throw new Error(data.detail || 'Login failed!');
        }
    } catch(err) {
        errText.innerText = err.message === 'Failed to fetch' ? 'Failed to connect FastAPI backend' : err.message;
        errBox.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-80', 'cursor-not-allowed');
        btnText.innerText = 'Sign In';
        btnSpinner.classList.add('hidden');
    }
});