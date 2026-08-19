<!DOCTYPE html>
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyperionOS</title>
    <link rel="stylesheet" href="assets/css/tailwind.css">
    <link rel="stylesheet" href="assets/css/fontawesome.min.css">
</head>
<body class="bg-slate-950 text-slate-100 font-sans flex h-screen overflow-hidden selection:bg-indigo-500 selection:text-white">

    <!-- SIDEBAR -->
    <?php include 'includes/sidebar.php'; ?>

    <!-- MAIN CONTENT AREA -->
    <main class="flex-1 overflow-y-auto bg-slate-950 p-8 lg:p-10">
        <?php include 'includes/sections/home.php'; ?>
        <?php include 'includes/sections/websites.php'; ?>
        <?php include 'includes/sections/database.php'; ?>
        <?php include 'includes/sections/docker.php'; ?>
        <?php include 'includes/sections/firewall.php'; ?>
        <?php include 'includes/sections/files.php'; ?>
        <?php include 'includes/sections/cloudflared.php'; ?>
        <?php include 'includes/sections/settings.php'; ?>
    </main>

    <!-- JS MODULES -->
    <script src="assets/js/app.js"></script>
    <script src="assets/js/home.js"></script>
    <script src="assets/js/websites.js"></script>
    <script src="assets/js/database.js"></script>
    <script src="assets/js/docker.js"></script>
    <script src="assets/js/firewall.js"></script>
    <script src="assets/js/files.js"></script>
    <script src="assets/js/cloudflared.js"></script>
</body>
</html>