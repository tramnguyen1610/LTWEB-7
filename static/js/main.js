// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {

    // --- 1. XỬ LÝ MENU DROPDOWN ĐĂNG XUẤT ---
    const userBtn = document.getElementById('userMenuBtn');
    const logoutDrop = document.getElementById('logoutDropdown');

    if (userBtn && logoutDrop) {
        userBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Ngăn click lan ra ngoài
            logoutDrop.classList.toggle('show');
            console.log("Đã click vào Avatar");
        });

        // Click bất cứ đâu ngoài Avatar để đóng menu
        document.addEventListener('click', function(event) {
            if (!userBtn.contains(event.target)) {
                logoutDrop.classList.remove('show');
            }
        });
    }

    // --- 2. XỬ LÝ SIDEBAR (CHẤM CÔNG, LƯƠNG...) ---
    const navToggles = document.querySelectorAll('.nav-toggle');
    navToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target');
            const targetSubmenu = document.getElementById(targetId);

            // Đóng các menu con khác đang mở
            document.querySelectorAll('.submenu').forEach(sub => {
                if (sub.id !== targetId) sub.classList.remove('show');
            });

            // Bật/tắt menu vừa click
            if (targetSubmenu) {
                targetSubmenu.classList.toggle('show');
            }
        });
    });
});