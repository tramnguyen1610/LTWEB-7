const DAY_NAMES = ["Thứ hai","Thứ ba","Thứ tư","Thứ năm","Thứ sáu","Thứ bảy","Chủ nhật"];

let currentWeekId = null;
let currentWeekData = null;
let currentEmployeesData = [];
let pendingDelete = null;
let currentWeekKey = null;
let selectedEmployeeId = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function filterWeeks() {
    const fromDate = document.getElementById('filterDateFrom').value;
    const toDate = document.getElementById('filterDateTo').value;
    const week = document.getElementById('filterWeek').value;

    const params = new URLSearchParams();
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    if (week) params.append('week', week);

    try {
        const res = await fetch(`${API_DELETE_WEEKS_URL}?${params.toString()}`);
        const data = await res.json();

        if (data.status !== 'success') {
            showToast(data.message || 'Không tải được danh sách tuần');
            return;
        }

        renderWeeks(data.weeks || []);
    } catch (err) {
        console.error(err);
        showToast('Lỗi tải danh sách tuần');
    }
}

function resetFilter() {
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    document.getElementById('filterWeek').value = '';
    filterWeeks();
}

function renderWeeks(weeks) {
    const list = document.getElementById('weeksList');
    list.innerHTML = '';

    if (!weeks.length) {
        list.innerHTML = '<div class="empty-state">Không tìm thấy tuần nào phù hợp.</div>';
        return;
    }

    weeks.forEach(w => {
        const card = document.createElement('div');
        card.className = 'week-card';
        card.innerHTML = `
            <div class="week-badge">${w.label}</div>
            <div class="week-info">
                <div class="week-range">${w.range}</div>
                <div class="week-meta">${w.employees} nhân viên đã đăng ký • ${w.shifts} ca làm</div>
            </div>
            <div class="week-status ${w.status === 'active' ? 'active' : 'upcoming'}">
                <span class="dot"></span>
                <span>${w.status === 'active' ? 'Đang hoạt động' : 'Sắp diễn ra'}</span>
            </div>
            <span class="week-arrow">→</span>
        `;
        card.onclick = () => openDetail(w.id);
        list.appendChild(card);
    });
}

async function openDetail(weekId) {
    currentWeekId = weekId;
    await loadWeekDetail();
    document.getElementById('screen-weeks').style.display = 'none';
    document.getElementById('screen-detail').style.display = 'block';
}
async function loadWeekDetail() {
    const searchName = document.getElementById('searchEmp').value.trim();
    const params = new URLSearchParams();
    if (searchName) params.append('name', searchName);

    try {
        const res = await fetch(`${API_DELETE_WEEK_DETAIL_BASE}${currentWeekId}/?${params.toString()}`);
        const data = await res.json();

        if (data.status !== 'success') {
            showToast(data.message || 'Không tải được chi tiết tuần');
            return;
        }

        ccurrentWeekData = data.week;
        currentEmployeesData = data.employees_data || [];
        currentWeekKey = data.week.week_key || null;

        document.getElementById('detail-week-label').textContent =
            `${data.week.label} (${data.week.range})`;

        renderEmployees(currentEmployeesData);
    } catch (err) {
        console.error(err);
        showToast('Lỗi tải chi tiết tuần');
    }
}

function renderEmployees(emps) {
    const container = document.getElementById('empCards');
    container.innerHTML = '';

    if (!emps.length) {
        container.innerHTML = '<div class="empty-state">Không có nhân viên nào trong tuần này.</div>';
        return;
    }

    emps.forEach(emp => {
        const card = document.createElement('div');
        card.className = 'emp-card';
        card.dataset.empId = emp.id;

        const daysHtml = emp.days.map((shift, i) => {
            const has = shift && shift.trim() !== '';
            return `
                <div class="day-chip ${has ? 'has-shift' : 'empty'}"
                     data-emp="${emp.id}"
                     data-day="${i}"
                     onclick="toggleDay(this)">
                    <span class="day-name">${DAY_NAMES[i]}</span>
                    <span class="shift-type">${has ? shift : '–'}</span>
                </div>
            `;
        }).join('');

        card.innerHTML = `
            <div class="emp-card-header">
                <div class="emp-avatar">${emp.avatar}</div>
                <div class="emp-info">
                    <div class="emp-name">${emp.name}</div>
                    <div class="emp-role">${emp.code} · ${emp.role}</div>
                </div>
                <button type="button" class="btn-delete-emp" onclick="askDeleteEmployee('${emp.id}')">🗑</button>
            </div>
            <div class="days-row">${daysHtml}</div>
        `;

        container.appendChild(card);
    });
}

function filterEmployees() {
    loadWeekDetail();
}

function toggleDay(el) {
    if (el.classList.contains('empty')) return;
    el.classList.toggle('selected');
}
function askDeleteEmployee(empId) {
    const emp = currentEmployeesData.find(e => String(e.id) === String(empId));
    if (!emp) return;

    selectedEmployeeId = empId;

    const selectedDays = Array.from(
        document.querySelectorAll(`[data-emp="${empId}"].selected`)
    ).map(c => parseInt(c.dataset.day));

    if (selectedDays.length > 0) {
        document.getElementById('modalTitle').textContent = 'Xóa ngày đã chọn';
        document.getElementById('modalMsg').textContent =
            `Bạn có chắc muốn xóa lịch làm các ngày: ${selectedDays.map(i => DAY_NAMES[i]).join(', ')} của nhân viên ${emp.name}?`;

        pendingDelete = {
            type: 'days',
            week_key: currentWeekKey,
            employee_id: empId,
            days: selectedDays
        };
    } else {
        document.getElementById('modalTitle').textContent = 'Xóa toàn bộ lịch tuần';
        document.getElementById('modalMsg').textContent =
            `Bạn có chắc muốn xóa toàn bộ lịch làm tuần này của nhân viên ${emp.name}?`;

        pendingDelete = {
            type: 'employee',
            week_key: currentWeekKey,
            employee_id: empId
        };
    }

    document.getElementById('modalOverlay').classList.add('show');
}

async function confirmDelete() {
    if (!pendingDelete) return;

    if (!pendingDelete.employee_id || !pendingDelete.week_key) {
        closeModal();
        showToast('Thiếu employee_id hoặc week_key');
        return;
    }

    try {
        const res = await fetch(API_DELETE_REMOVE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(pendingDelete)
        });

        const data = await res.json();
        closeModal();

        if (data.status !== 'success') {
            showToast(data.message || 'Xóa thất bại');
            return;
        }

        showToast(data.message || 'Xóa thành công');
        await loadWeekDetail();
    } catch (err) {
        console.error(err);
        closeModal();
        showToast('Lỗi khi xóa dữ liệu');
    } finally {
        pendingDelete = null;
    }
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('show');
}

function backToWeeks() {
    document.getElementById('screen-detail').style.display = 'none';
    document.getElementById('screen-weeks').style.display = 'block';
    filterWeeks();
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    filterWeeks();
});

window.filterWeeks = filterWeeks;
window.resetFilter = resetFilter;
window.openDetail = openDetail;
window.filterEmployees = filterEmployees;
window.toggleDay = toggleDay;
window.askDeleteEmployee = askDeleteEmployee;
window.confirmDelete = confirmDelete;
window.closeModal = closeModal;
window.backToWeeks = backToWeeks;