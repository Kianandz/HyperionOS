function openModal(id) { document.getElementById(id).classList.remove('hidden'); }
    function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

    function confirmWebDelete(domain) {
        Swal.fire({
            title: 'Hapus website ini?', text: domain, icon: 'warning',
            showCancelButton: true, background: '#0f172a', color: '#fff',
            confirmButtonColor: '#e11d48', confirmButtonText: 'Hapus!'
        }).then((res) => {
            if (res.isConfirmed) document.getElementById(`formDelete-${domain}`).submit();
        });
    }