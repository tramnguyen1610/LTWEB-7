// static/js/ket_qua_tinh_luong.js
document.addEventListener('DOMContentLoaded', function() {
    const btnSave = document.getElementById('btnSave');
    if (!btnSave) return;

    btnSave.addEventListener('click', function() {
        const period = btnSave.getAttribute('data-period');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = btnSave.getAttribute('data-url');
        const redirectUrl = btnSave.getAttribute('data-redirect');

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'period=' + encodeURIComponent(period)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                window.location.href = redirectUrl;
            } else {
                alert('❌ Lỗi: ' + data.message);
            }
        })
        .catch(error => {
            alert('⚠️ Có lỗi xảy ra khi lưu. Vui lòng thử lại.');
        });
    });
});