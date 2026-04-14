document.addEventListener('DOMContentLoaded', function() {

    // 1. Xử lý Menu con (Submenu)
    const navToggles = document.querySelectorAll('.nav-toggle');
    const allSubmenus = document.querySelectorAll('.submenu');

    navToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault(); // Ngăn trang bị nhảy lên đầu

            const targetId = this.getAttribute('data-target');
            const targetSubmenu = document.getElementById(targetId);

            // Đóng các menu khác
            allSubmenus.forEach(sub => {
                if (sub.id !== targetId) sub.classList.remove('show');
            });

            // Bật/Tắt menu hiện tại
            targetSubmenu.classList.toggle('show');
        });
    });

    // 2. Xử lý Dropdown Đăng xuất
    const userBtn = document.getElementById('userMenuBtn');
    const logoutDrop = document.getElementById('logoutDropdown');

    if (userBtn) {
        userBtn.addEventListener('click', function(e) {
            logoutDrop.classList.toggle('show');
            e.stopPropagation();
        });

        document.addEventListener('click', () => logoutDrop.classList.remove('show'));
    }

    // 3. Tự động ẩn Alert
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(a => a.style.display = 'none');
    }, 3000);
});