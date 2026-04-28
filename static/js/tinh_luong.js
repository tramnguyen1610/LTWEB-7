document.addEventListener('DOMContentLoaded', function() {
    const monthSelect = document.getElementById('monthSelect');
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // Tháng trong JS chạy từ 0-11

    // Tạo danh sách cho 2 năm (Năm hiện tại và năm trước đó)
    for (let year = currentYear; year >= currentYear - 1; year--) {
        // Nếu là năm hiện tại thì chỉ lấy đến tháng hiện tại, nếu năm trước thì lấy đủ 12 tháng
        let startMonth = (year === currentYear) ? currentMonth : 12;

        for (let month = startMonth; month >= 1; month--) {
            const monthStr = month < 10 ? '0' + month : month;
            const periodValue = `${monthStr}-${year}`;
            const displayLabel = `Tháng ${month} - ${year}`;

            const option = document.createElement('option');
            option.value = periodValue;
            option.textContent = displayLabel;
            monthSelect.appendChild(option);
        }
    }
});
// Hàm format tiền VND
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount) + 'đ';
}

// 1. Hàm gọi API Preview dữ liệu khi chọn tháng
async function loadPreview() {
    const period = document.getElementById('monthSelect').value;
    const previewCard = document.getElementById('previewCard');

    if (!period) {
        previewCard.classList.remove('show');
        return;
    }

    try {
        // Dòng 29, sửa lại thành:
const response = await fetch(`/luong/api/preview-tinh-luong/?period=${period}`);
        const data = await response.json();

        if (data.error) {
            alert("Lỗi: " + data.error);
            return;
        }

        // Đổ dữ liệu thật từ Django vào 3 card
        document.getElementById('totalEmployees').textContent = data.total_employees;
        document.getElementById('totalHours').textContent = data.total_hours + ' giờ';
        document.getElementById('estimatedTotal').textContent = formatCurrency(data.total_estimated);

        previewCard.classList.add('show');
    } catch (error) {
        console.error("Lỗi fetch preview:", error);
    }
}

// 2. Hàm xử lý khi bấm nút "Bắt đầu tính"
async function startCalculate() {
    const period = document.getElementById('monthSelect').value;
    if (!period) {
        alert("Vui lòng chọn tháng.");
        return;
    }
    window.location.href = `/luong/ket-qua-tinh-luong/?period=${period}`;
}