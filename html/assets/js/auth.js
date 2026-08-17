document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const errBox = document.getElementById('login-error');
            errBox.classList.add('hidden');

            try {
                const res = await fetch('http://localhost:8000/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value
                    })
                });

                const data = await res.json();

                if (res.ok) {
                    localStorage.setItem('hyperion_user', data.user);
                    window.location.href = 'dashboard.php';
                } else {
                    errBox.innerText = data.detail || 'Login gagal!';
                    errBox.classList.remove('hidden');
                }
            } catch(err) {
                errBox.innerText = 'Gagal terhubung ke FastAPI backend';
                errBox.classList.remove('hidden');
            }
        });