let allData = [];
let pendingAction = null;

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

async function loadApproveData() {
    const name = document.getElementById('fName').value.trim();
    const monthYear = document.getElementById('fMonth').value;
    const week = document.getElementById('fWeek').value;
    const shiftType = document.getElementById('fCa').value;

    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (monthYear) params.append('month_year', monthYear);
    if (week) params.append('week', week);
    if (shiftType) params.append('shift_type', shiftType);

    try {
        const res = await fetch(`${API_APPROVE_LIST_URL}?${params.toString()}`);
        const data = await res.json();

        if (data.status !== 'success') {
            showToast('❌', data.message || 'Không tải được dữ liệu');
            return;
        }

        allData = data.rows || [];
        renderTable(allData);
        updateStats(data.stats);
    } catch (err) {
        console.error(err);
        showToast('❌', 'Lỗi tải dữ liệu');
    }
}

function doSearch() {
    loadApproveData();
}

function doReset() {
    document.getElementById('fName').value = '';
    document.getElementById('fMonth').value = '';
    document.getElementById('fWeek').value = '';
    document.getElementById('fCa').value = '';
    loadApproveData();
}

function updateStats(stats) {
    document.getElementById('statTotal').textContent = stats.total || 0;
    document.getElementById('statApproved').textContent = stats.approved || 0;
    document.getElementById('statPending').textContent = stats.pending || 0;
    document.getElementById('statRejected').textContent = stats.rejected || 0;
}

async function updateStatus(employeeId, action) {
    const monthYear = document.querySelector('[name="month_year"]').value;
    const week = document.querySelector('[name="week"]').value;

    const res = await fetch(API_APPROVE_UPDATE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            employee_id: employeeId,
            action: action,
            month_year: monthYear,
            week: week
        })
    });

    const data = await res.json();

    if (data.status === 'success') {
        showToast('Cập nhật thành công');
        loadData(); // reload lại bảng
    } else {
        showToast(data.message);
    }
}

function renderTable(rows) {
    const tbody = document.getElementById('tableBody');
    const noResult = document.getElementById('noResult');

    if (!rows.length) {
        tbody.innerHTML = '';
        noResult.style.display = 'block';
        return;
    }

    noResult.style.display = 'none';

    tbody.innerHTML = rows.map(r => {
        let badge = '';
        if (r.status === 'APPROVED') {
            badge = `<span class="badge badge-approved">Đã duyệt</span>`;
        } else if (r.status === 'REJECTED') {
            badge = `<span class="badge badge-rejected">Từ chối</span>`;
        } else {
            badge = `<span class="badge badge-pending">Đang chờ</span>`;
        }

        const actions = r.status === 'PENDING'
            ? `<div class="action-btns">
                    <button class="btn-duyet" type="button" onclick="openConfirm(${r.id}, 'approve')">Duyệt</button>
                    <button class="btn-tuchoi" type="button" onclick="openConfirm(${r.id}, 'reject')">Từ chối</button>
               </div>`
            : `<span class="dash">——</span>`;

        return `
            <tr>
                <td>
                    <span class="emp-code">${r.code}</span>
                    <span class="emp-name">${r.name}</span>
                </td>
                <td>${String(r.days).padStart(2, '0')}</td>
                <td>${r.hours} giờ</td>
                <td>${r.reg_time}</td>
                <td>${badge}</td>
                <td>${actions}</td>
            </tr>
        `;
    }).join('');
}

function openConfirm(employeeId, type) {
    const rec = allData.find(r => r.id === employeeId);
    if (!rec) return;

    pendingAction = { employeeId, type };

    if (type === 'approve') {
        document.getElementById('cIcon').textContent = '✅';
        document.getElementById('cTitle').textContent = 'Xác nhận duyệt';
        document.getElementById('cDesc').textContent = `Bạn có chắc muốn duyệt lịch làm việc của ${rec.name}?`;
        const btn = document.getElementById('cConfirmBtn');
        btn.className = 'cbtn cbtn-confirm-green';
        btn.textContent = 'Duyệt ngay';
    } else {
        document.getElementById('cIcon').textContent = '❌';
        document.getElementById('cTitle').textContent = 'Xác nhận từ chối';
        document.getElementById('cDesc').textContent = `Bạn có chắc muốn từ chối lịch làm việc của ${rec.name}?`;
        const btn = document.getElementById('cConfirmBtn');
        btn.className = 'cbtn cbtn-confirm-red';
        btn.textContent = 'Từ chối ngay';
    }

    document.getElementById('confirmModal').classList.add('show');
}

function closeConfirm() {
    document.getElementById('confirmModal').classList.remove('show');
    pendingAction = null;
}
async function executeAction() {
    if (!pendingAction) return;

    const actionType = pendingAction.type;
    const employeeId = pendingAction.employeeId;

    try {
        const res = await fetch(API_APPROVE_UPDATE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                employee_id: employeeId,
                action: actionType
            })
        });

        const data = await res.json();

        if (data.status !== 'success') {
            closeConfirm();
            showToast('❌', data.message || 'Cập nhật thất bại');
            return;
        }

        closeConfirm();

        showToast(
            actionType === 'approve' ? '✅' : '❌',
            actionType === 'approve'
                ? 'Đã duyệt thành công'
                : 'Đã từ chối thành công'
        );

        loadApproveData();
    } catch (err) {
        console.error(err);
        closeConfirm();
        showToast('❌', 'Lỗi cập nhật dữ liệu');
    }
}

function showToast(icon, msg) {
    document.getElementById('toastIcon').textContent = icon;
    document.getElementById('toastMsg').textContent = msg;
    const t = document.getElementById('toast');
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3200);
}

window.doSearch = doSearch;
window.doReset = doReset;
window.openConfirm = openConfirm;
window.closeConfirm = closeConfirm;
window.executeAction = executeAction;

document.addEventListener('DOMContentLoaded', function () {
    loadApproveData();
});