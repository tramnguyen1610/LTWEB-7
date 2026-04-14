// Tự động nhận dữ liệu thật từ Django
let rawData = window.DJANGO_DATA || [];
let filteredData = [...rawData];

const ROWS_PER_PAGE = 7;
let currentPage = 1;

// ── RENDER BẢNG ──
function renderTable() {
    const tbody = document.getElementById('tableBody');
    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const page = filteredData.slice(start, start + ROWS_PER_PAGE);

    tbody.innerHTML = page.map((r, i) => `
      <tr>
        <td>
          <div style="font-weight: 600; font-size: 13px;">${r.day}</div>
          <div style="font-size: 12px; color: #6B7280;">${r.date}</div>
        </td>
        <td>
          <div style="color: #1d6fa8; font-weight: 600; font-size: 12.5px;">${r.id}</div>
          <div style="font-size: 13px;">${r.name}</div>
        </td>
        <td>${r.in}</td>
        <td>${r.out}</td>
        <td>${r.hours}</td>
        <td><span class="badge ${r.status === 'Đúng giờ' ? 'badge-green' : 'badge-red'}">${r.status}</span></td>
        <td>
          <div class="actions">
            <button class="action-btn" style="background: #dbeafe; color: #1e40af;" title="Xem chi tiết" onclick="viewRow(${start + i})">👁</button>
          </div>
        </td>
      </tr>
    `).join('');

    renderPagination();
}

// ── TÌM KIẾM & LỌC ──
function filterTable() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    filteredData = rawData.filter(r =>
      r.name.toLowerCase().includes(q) || r.id.toLowerCase().includes(q)
    );
    currentPage = 1;
    renderTable();
}

function toggleMonthList() {
    document.getElementById('monthDropdownList').classList.toggle('open');
}

function pickMonth(num, label) {
    document.getElementById('monthSelectLabel').textContent = label;
    document.querySelectorAll('.month-option').forEach((el, i) => {
        el.classList.toggle('selected', i === num);
    });
    document.getElementById('monthDropdownList').classList.remove('open');

    const q = document.getElementById('searchInput').value.toLowerCase();
    filteredData = rawData.filter(r => {
        const matchQ = r.name.toLowerCase().includes(q) || r.id.toLowerCase().includes(q);
        if (num === 0) return matchQ;
        const month = parseInt(r.date.split('/')[1]);
        return matchQ && month === num;
    });
    currentPage = 1;
    renderTable();
}

// ── PHÂN TRANG ──
function renderPagination() {
    const total = Math.ceil(filteredData.length / ROWS_PER_PAGE);
    const pg = document.getElementById('pagination');
    if (total <= 1) { pg.innerHTML = ''; return; }

    let html = `<button class="page-btn" onclick="goPage(${currentPage - 1})">Trước</button>`;
    for (let i = 1; i <= total; i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goPage(${i})">${i}</button>`;
    }
    html += `<button class="page-btn" onclick="goPage(${currentPage + 1})">Tiếp</button>`;
    pg.innerHTML = html;
}

function goPage(n) {
    const total = Math.ceil(filteredData.length / ROWS_PER_PAGE);
    if (n < 1 || n > total) return;
    currentPage = n;
    renderTable();
}

// ── MODAL XEM CHI TIẾT ──
function viewRow(idx) {
    const r = filteredData[idx];

    document.getElementById('vId').textContent = r.id;
    document.getElementById('vName').textContent = r.name;
    document.getElementById('vDate').textContent = `${r.day}, ${r.date}`;
    document.getElementById('vIn').textContent = r.in;
    document.getElementById('vOut').textContent = r.out;
    document.getElementById('vHours').textContent = r.hours;
    document.getElementById('vStatus').textContent = r.status;

    document.getElementById('viewOverlay').classList.add('open');
}

function closeView() {
    document.getElementById('viewOverlay').classList.remove('open');
}

function closeViewOutside(e) {
    if (e.target === document.getElementById('viewOverlay')) closeView();
}

// ── KHỞI TẠO ──
document.addEventListener('DOMContentLoaded', function() {
    renderTable();
});

// Đóng dropdown chọn tháng khi click ra ngoài
document.addEventListener('click', function(e) {
    const wrap = document.getElementById('monthSelectWrap');
    const dropdown = document.getElementById('monthDropdownList');
    if (wrap && dropdown && !wrap.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});