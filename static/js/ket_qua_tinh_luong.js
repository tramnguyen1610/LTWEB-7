document.addEventListener('DOMContentLoaded', function() {
    const btnSave = document.getElementById('btnSave');
    if (!btnSave) return;

    // Hàm gọi Toast Thông báo
    function showToast(message, isSuccess = true) {
        const toast = document.getElementById('customToast');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = document.querySelector('.toast-icon i');

        toastMessage.textContent = message;

        if (isSuccess) {
            toast.classList.remove('error');
            toastIcon.className = 'fa-solid fa-circle-check';
            toastIcon.style.color = '#27ae60';
        } else {
            toast.classList.add('error');
            toastIcon.className = 'fa-solid fa-circle-exclamation';
            toastIcon.style.color = '#e74c3c';
        }

        toast.classList.add('show');
    }

    btnSave.addEventListener('click', function() {
        const period = btnSave.getAttribute('data-period');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = btnSave.getAttribute('data-url');
        const redirectUrl = btnSave.getAttribute('data-redirect');

        // Đổi text nút thành Đang lưu
        btnSave.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
        btnSave.disabled = true;

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
                showToast(data.message, true);

                // Đợi 2 giây cho người dùng đọc xong rồi mới chuyển trang
                setTimeout(() => {
                    window.location.href = redirectUrl + "?period=" + period;
                }, 2000);
            } else {
                showToast(data.message, false);
                btnSave.innerHTML = '💾 Lưu bảng lương';
                btnSave.disabled = false;
            }
        })
        .catch(error => {
            showToast('Có lỗi xảy ra khi lưu. Vui lòng thử lại.', false);
            btnSave.innerHTML = '💾 Lưu bảng lương';
            btnSave.disabled = false;
        });
    });
});