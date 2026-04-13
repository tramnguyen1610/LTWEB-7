// static/js/main.js
// Tự động ẩn alert sau 3 giây
setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 3000);

// Active menu dựa trên URL hiện tại
document.addEventListener('DOMContentLoaded', function() {
    let currentPath = window.location.pathname;
    let navLinks = document.querySelectorAll('.sidebar .nav-link');

    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});