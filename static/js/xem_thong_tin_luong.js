let currentEmployees = [];
let filteredEmployees = [];
let currentPage = 1;
const rowsPerPage = 7;

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount) + 'đ';
}

// Tự động sinh danh sách tháng (2 năm gần nhất)
function initMonthSelect() {
    const monthSelect = document.getElementById('monthSelect');
    monthSelect.innerHTML = '';
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    for (let year = currentYear; year >= currentYear - 1; year--) {
        let startMonth = (year === currentYear) ? currentMonth : 12;
        for (let month = startMonth; month >= 1; month--) {
            const monthStr = month < 10 ? '0' + month : month;
            const periodValue = `${monthStr}-${year}`;
            const displayLabel = `Tháng ${month}, ${year}`;
            monthSelect.innerHTML += `<option value="${periodValue}">${displayLabel}</option>`;
        }
    }
}

// Lấy dữ liệu thật từ Django
async function loadDataByMonth() {
    const selectedPeriod = document.getElementById('monthSelect').value; // 'MM-YYYY'
    document.getElementById('searchInput').value = "";
    currentPage = 1;

    // Hiển thị loading mờ
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 30px;"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải dữ liệu...</td></tr>';

    try {
        const response = await fetch(`/salary/api/danh-sach-luong/?period=${selectedPeriod}`);
        const result = await response.json();

        currentEmployees = result.data || [];
        filteredEmployees = [...currentEmployees];
        renderTable(filteredEmployees);
    } catch (error) {
        console.error("Lỗi:", error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: red;">Lỗi tải dữ liệu.</td></tr>';
    }
}

function renderTable(data) {
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = '';

    if(data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 30px; color: #666;">Chưa có dữ liệu bảng lương trong kỳ này. Vui lòng vào mục "Tính lương" trước.</td></tr>';
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = data.slice(start, end);

    paginatedData.forEach(emp => {
        tbody.innerHTML += `
            <tr onclick="openModal('${emp.id}')">
                <td style="font-weight: 600;">${emp.id}</td>
                <td class="td-name">${emp.name}</td>
                <td>${emp.role}</td>
                <td>${formatCurrency(emp.base_salary)}</td>
                <td class="td-salary">${formatCurrency(emp.total_salary)}</td>
            </tr>
        `;
    });

    renderPagination(data.length);
}

function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / rowsPerPage);
    const paginationContainer = document.getElementById('paginationContainer');

    if (totalItems <= rowsPerPage) {
        paginationContainer.innerHTML = '';
        return;
    }

    let html = `<button class="page-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled style="opacity:0.5;cursor:not-allowed;"' : ''}>[Trước]</button>`;
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="page-btn ${currentPage === i ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }
    html += `<button class="page-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled style="opacity:0.5;cursor:not-allowed;"' : ''}>[Tiếp]</button>`;
    paginationContainer.innerHTML = html;
}

function changePage(page) {
    const totalPages = Math.ceil(filteredEmployees.length / rowsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTable(filteredEmployees);
}

function filterTable() {
    const keyword = document.getElementById('searchInput').value.toLowerCase();
    filteredEmployees = currentEmployees.filter(emp =>
        emp.name.toLowerCase().includes(keyword) ||
        emp.id.toLowerCase().includes(keyword)
    );
    currentPage = 1;
    renderTable(filteredEmployees);
}

function openModal(id) {
    const emp = currentEmployees.find(e => e.id === id);
    if(!emp) return;

    const currentMonthLabel = document.getElementById('monthSelect').options[document.getElementById('monthSelect').selectedIndex].text;

    document.getElementById('m-avatar').src = emp.avatar;
    document.getElementById('m-name').textContent = emp.name;
    document.getElementById('m-id').textContent = emp.id;
    // Thêm Level Name vào cạnh Role
    document.getElementById('m-role').textContent = `${emp.role} - ${emp.level_name}`;
    document.getElementById('m-month').textContent = currentMonthLabel;

    document.getElementById('m-rate').textContent = formatCurrency(emp.rate) + '/giờ';
    document.getElementById('m-hours').textContent = emp.hours;

    document.getElementById('m-base').textContent = formatCurrency(emp.base_salary);
    document.getElementById('m-bonus').textContent = '+' + formatCurrency(emp.bonus);
    document.getElementById('m-penalty').textContent = '-' + formatCurrency(emp.penalty);
    document.getElementById('m-total').textContent = formatCurrency(emp.total_salary);

    document.getElementById('salaryModal').classList.add('show');
}

function closeModal() {
    document.getElementById('salaryModal').classList.remove('show');
}

// Khởi chạy khi load trang
// Khởi chạy khi load trang
document.addEventListener('DOMContentLoaded', () => {
    initMonthSelect();

    // ĐỌC THÁNG TỪ URL (NẾU CÓ) ĐỂ TỰ ĐỘNG CHỌN
    const urlParams = new URLSearchParams(window.location.search);
    const periodFromUrl = urlParams.get('period');

    if (periodFromUrl) {
        // Nếu có truyền tháng qua URL thì gán vào ô chọn
        document.getElementById('monthSelect').value = periodFromUrl;
    }

    // Sau khi chọn đúng tháng rồi mới load dữ liệu
    loadDataByMonth();
});