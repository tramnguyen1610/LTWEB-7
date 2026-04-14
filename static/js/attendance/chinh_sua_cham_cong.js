let rawData = window.DJANGO_DATA || [];
let processedData = [];
let filteredData = [];
let activeShiftTab = 'Tất cả';

// Phân trang
const ROWS_PER_PAGE = 7;
let currentPage = 1;

function showToast(msg, bg = '#16A34A') {
    const el = document.getElementById('toast');
    if(!el) return; el.textContent = msg; el.style.background = bg;
    el.classList.add('show'); setTimeout(() => el.classList.remove('show'), 3000);
}

function closeModal(modalId) { document.getElementById(modalId).classList.remove('open'); }
function closeModalOutside(e, modalId) { if (e.target.id === modalId) closeModal(modalId); }

function enrichData() {
    processedData = rawData.map(r => {
        let shift = 'Chưa rõ'; let status = 'Đúng giờ';
        if (!r.in || r.in === '--:--' || parseFloat(r.hours) === 0) return { ...r, shift: 'Chưa rõ', autoStatus: 'Vắng mặt' };
        const [h, m] = r.in.split(':').map(Number);
        const timeInMins = h * 60 + m;
        if (timeInMins < 12 * 60) { shift = 'Ca Sáng'; if (timeInMins > (7 * 60 + 30)) status = 'Muộn giờ'; }
        else if (timeInMins < 17 * 60) { shift = 'Ca Chiều'; if (timeInMins > (12 * 60 + 30)) status = 'Muộn giờ'; }
        else { shift = 'Ca Tối'; if (timeInMins > (17 * 60 + 30)) status = 'Muộn giờ'; }
        let finalStatus = (r.status !== 'Đúng giờ' && r.status !== 'Vắng mặt') ? r.status : status;
        return { ...r, shift, autoStatus: finalStatus };
    });
    filteredData = [...processedData];
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    if (filteredData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:40px; color:#9CA3AF;">📭 Không tìm thấy dữ liệu.</td></tr>`;
        document.getElementById('pagination').innerHTML = ''; return;
    }

    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const end = start + ROWS_PER_PAGE;
    const pageData = filteredData.slice(start, end);

    tbody.innerHTML = pageData.map((r, i) => {
        const actualIndex = start + i;
        let badgeClass = 'badge-green';
        if (r.autoStatus === 'Vắng mặt') badgeClass = 'badge-red';
        if (r.autoStatus === 'Muộn giờ' || r.autoStatus === 'Về sớm') badgeClass = 'badge-warning';

        return `
        <tr>
            <td><div style="font-weight: 600;">${r.day}</div><div style="font-size: 11px; color: #6B7280;">${r.date}</div></td>
            <td><div style="color: #8B1A2B; font-weight: 600;">${r.id}</div><div style="font-size: 12px;">${r.name}</div></td>
            <td><span class="badge badge-gray">${r.shift}</span></td>
            <td style="font-weight: 600;">${r.in}</td>
            <td style="font-weight: 600;">${r.out}</td>
            <td><span class="badge ${badgeClass}">${r.autoStatus}</span></td>
            <td style="text-align: center;">
                <div class="actions">
                    <button class="action-btn" onclick="openHistoryModal(${actualIndex})" title="Lịch sử">🕐</button>
                    <button class="action-btn" onclick="openViewModal(${actualIndex})" title="Xem">👁</button>
                    <button class="action-btn" onclick="openEditModal(${actualIndex})" title="Sửa">✏️</button>
                </div>
            </td>
        </tr>`;
    }).join('');
    renderPagination();
}

function renderPagination() {
    const totalPages = Math.ceil(filteredData.length / ROWS_PER_PAGE);
    const pag = document.getElementById('pagination');
    if (totalPages <= 1) { pag.innerHTML = ''; return; }
    let html = `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">[Trước]</button>`;
    for (let i = 1; i <= totalPages; i++) { html += `<button class="page-btn ${currentPage === i ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`; }
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">[Tiếp]</button>`;
    pag.innerHTML = html;
}

function goToPage(page) { currentPage = page; renderTable(); }

function setShiftTab(shiftName, btnElement) {
    activeShiftTab = shiftName;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');
    filterTable();
}

function toggleMonthList() { document.getElementById('monthDropdownList').classList.toggle('open'); }
function pickMonth(num, label) {
    document.getElementById('monthSelectLabel').textContent = label;
    document.getElementById('monthDropdownList').classList.remove('open');
    filterTable();
}

function filterTable() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    const monthText = document.getElementById('monthSelectLabel').textContent;
    let selectedMonth = 0;
    if (monthText.includes('Tháng')) selectedMonth = parseInt(monthText.replace('Tháng ', ''));
    filteredData = processedData.filter(r => {
        const matchSearch = r.name.toLowerCase().includes(q) || r.id.toLowerCase().includes(q);
        const matchMonth = (selectedMonth === 0) || (parseInt(r.date.split('/')[1]) === selectedMonth);
        const matchShift = (activeShiftTab === 'Tất cả') || (r.shift === activeShiftTab);
        return matchSearch && matchMonth && matchShift;
    });
    currentPage = 1; renderTable();
}

// Mấy hàm modal openViewModal, openHistoryModal, openEditModal... Linh giữ nguyên code cũ nhé!
function openViewModal(index) {
    const r = filteredData[index];
    document.getElementById('vName').textContent = `${r.id} - ${r.name}`;
    document.getElementById('vDate').textContent = `${r.day}, ${r.date}`;
    document.getElementById('vHours').textContent = r.hours;
    document.getElementById('vStatus').textContent = r.autoStatus;
    document.getElementById('viewOverlay').classList.add('open');
}

function openEditModal(index) {
    const r = filteredData[index];
    document.getElementById('mDbId').value = r.db_id;
    document.getElementById('mNhanVien').textContent = `${r.id} - ${r.name}`;
    document.getElementById('mNgay').textContent = `${r.day}, ${r.date}`;
    document.getElementById('mGioVaoHT').textContent = r.in;
    document.getElementById('mGioRaHT').textContent = r.out;
    document.getElementById('mTongGioHT').textContent = r.hours;
    document.getElementById('mTrangThaiHT').textContent = r.autoStatus;
    document.getElementById('mGioVaoNew').value = r.in !== '--:--' ? r.in : '';
    document.getElementById('mGioRaNew').value = r.out !== '--:--' ? r.out : '';
    document.getElementById('mTrangThaiNew').value = 'Tự động';
    document.getElementById('editModalOverlay').classList.add('open');
}

function calcHours() {
    const vao = document.getElementById('mGioVaoNew').value;
    const ra = document.getElementById('mGioRaNew').value;
    const tong = document.getElementById('mTongGioNew');
    if (vao && ra) {
        const [h1, m1] = vao.split(':').map(Number);
        const [h2, m2] = ra.split(':').map(Number);
        let diff = (h2 * 60 + m2) - (h1 * 60 + m1);
        if (diff < 0) diff += 24 * 60;
        tong.value = (diff / 60).toFixed(2) + ' giờ';
    } else { tong.value = ''; }
}

function saveEdit() { document.getElementById('confirmOverlay').classList.add('open'); }

async function confirmSave() {
    const db_id = document.getElementById('mDbId').value;
    const payload = { check_in: document.getElementById('mGioVaoNew').value, check_out: document.getElementById('mGioRaNew').value, reason: document.getElementById('mLyDo').value };
    try {
        const response = await fetch(`/cham-cong/api/update/${db_id}/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN }, body: JSON.stringify(payload) });
        const data = await response.json();
        if (data.success) { window.location.reload(); }
    } catch (error) { console.error(error); }
}

document.addEventListener('DOMContentLoaded', () => { enrichData(); renderTable(); });