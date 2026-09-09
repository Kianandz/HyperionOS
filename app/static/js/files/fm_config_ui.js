// Config SweetAlert2 (Main Theme)
const SwalDark = Swal.mixin({
    background: '#0f172a',
    color: '#f8fafc',
    confirmButtonColor: '#4f46e5',
    cancelButtonColor: '#334155',
    customClass: {
        popup: 'border border-slate-700 rounded-2xl shadow-2xl',
        confirmButton: 'rounded-lg px-5 py-2 font-semibold',
        cancelButton: 'rounded-lg px-5 py-2 font-medium'
    }
});

// Config Toast Notification 
const ToastDark = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 2500,
    timerProgressBar: true,
    background: '#1e293b',
    color: '#f8fafc',
    customClass: { popup: 'border border-slate-700/50 rounded-xl shadow-xl' }
});

// --- DROPDOWN LOGIC ---
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    if (dropdown.classList.contains('hidden')) {
        document.querySelectorAll('.dropdown-container > div:not(.hidden)').forEach(el => el.classList.add('hidden'));
        dropdown.classList.remove('hidden');
    } else {
        dropdown.classList.add('hidden');
    }
}

document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown-container')) {
        document.querySelectorAll('.dropdown-container > div:not(.hidden)').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
    }
});

// --- SEARCH & SORT ---
function searchTable() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const rows = document.querySelectorAll("#fileTableBody tr");
    rows.forEach(row => {
        const nameCell = row.querySelector("td:nth-child(2)");
        if (nameCell) {
            const text = nameCell.textContent.toLowerCase();
            row.style.display = text.includes(input) ? "" : "none";
        }
    });
}

let sortDirection = false;
function sortTable(columnIndex, isNumber = false) {
    const tbody = document.getElementById("fileTableBody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    
    sortDirection = !sortDirection;

    rows.sort((a, b) => {
        const cellA = a.querySelectorAll("td")[columnIndex];
        const cellB = b.querySelectorAll("td")[columnIndex];
        if (!cellA || !cellB) return 0;

        const valA = cellA.getAttribute("data-sort-val") || cellA.textContent.trim();
        const valB = cellB.getAttribute("data-sort-val") || cellB.textContent.trim();

        if (isNumber) {
            return sortDirection ? parseFloat(valA) - parseFloat(valB) : parseFloat(valB) - parseFloat(valA);
        } else {
            return sortDirection ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }
    });

    tbody.append(...rows);
}