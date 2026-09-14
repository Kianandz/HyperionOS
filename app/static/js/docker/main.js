document.addEventListener('click', (e) => {
    if (!e.target.closest('button[onclick^="toggleMenu"]') && !e.target.closest('[id^="menu-"]')) {
        document.querySelectorAll('[id^="menu-"]').forEach(menu => menu.classList.add('hidden'));
    }
});

function toggleMenu(menuId) {
    document.querySelectorAll('[id^="menu-"]').forEach(menu => {
        if (menu.id !== menuId) menu.classList.add('hidden');
    });
    const menu = document.getElementById(menuId);
    if (menu) menu.classList.toggle('hidden');
}

function confirmUninstall(event, formElement) {
    event.preventDefault();
    Swal.fire({
        title: 'Are you sure?',
        text: "This will completely delete the container along with its image!",
        icon: 'warning',
        showCancelButton: true,
        background: '#0f172a',
        color: '#f8fafc',
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#475569',
        confirmButtonText: '<i class="fa fa-solid fa-trash mr-1"></i> Yes, Delete!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) formElement.submit();
    });
}