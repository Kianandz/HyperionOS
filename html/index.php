<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - HyperionOS</title>
    <script>
        if (localStorage.getItem('hyperion_user')) {
            window.location.href = 'dashboard.php';
        }
    </script>

    <link rel="stylesheet" href="assets/css/tailwind.css">
    <link rel="stylesheet" href="assets/css/fontawesome.min.css">
</head>
<body class="bg-slate-950 text-slate-100 flex items-center justify-center h-screen">
    <div class="bg-slate-900 border border-slate-800 p-8 rounded-xl w-full max-w-md space-y-6">
        <div class="text-center space-y-2">
            <div class="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center font-bold text-2xl mx-auto">H</div>
            <h1 class="text-2xl font-bold text-white">Hyperion<span class="text-indigo-500">OS</span></h1>
            <p class="text-slate-400 text-sm">Log in with your credentials.</p>
        </div>

        <div id="login-error" class="hidden p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm rounded"></div>

        <form id="login-form" class="space-y-4">
            <div>
                <label class="block text-sm text-slate-400 mb-1">Username</label>
                <input type="text" id="username" required class="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <div>
                <label class="block text-sm text-slate-400 mb-1">Password</label>
                <input type="password" id="password" required class="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded transition">
                Login
            </button>
        </form>
    </div>

    <script src="assets/js/auth.js"></script>
</body>
</html>