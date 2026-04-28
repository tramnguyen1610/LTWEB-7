function updateDateTime() {
    const now = new Date();

    const time = now.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
    });

    const date = now.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });

    const timeEl = document.getElementById('currentTime');
    const dateEl = document.getElementById('currentDate');

    if (timeEl && dateEl) {
        timeEl.textContent = time;
        dateEl.textContent = date;
    }
}

updateDateTime();
setInterval(updateDateTime, 1000);