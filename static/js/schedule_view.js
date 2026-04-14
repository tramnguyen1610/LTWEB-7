function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

function getStatusIcon(status) {
    if (status === 'approved') {
        return '<span class="detail-status-icon detail-status-approved">✅</span>';
    }
    if (status === 'pending') {
        return '<span class="detail-status-icon detail-status-pending">🕒</span>';
    }
    if (status === 'rejected') {
        return '<span class="detail-status-icon detail-status-rejected">❌</span>';
    }
    return '<span class="detail-status-icon detail-status-off">—</span>';
}

function formatWeekLabel(item) {
    if (item.weekday) return item.weekday.toUpperCase();
    return '';
}

async function viewDetail(employeeId) {
    const monthYearEl = document.querySelector('select[name="month_year"]');
    const weekEl = document.querySelector('select[name="week"]');

    const monthYear = monthYearEl ? monthYearEl.value : '';
    const week = weekEl ? weekEl.value : '';

    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');

    modal.style.display = 'flex';
    modalBody.innerHTML = '<div>Đang tải...</div>';

    try {
        const url = `/schedule/api/xem-lich/${employeeId}/?month_year=${encodeURIComponent(monthYear)}&week=${encodeURIComponent(week)}`;
        const res = await fetch(url);
        const data = await res.json();

        if (data.status !== 'success') {
            modalBody.innerHTML = `<div style="color:red;">${data.message || 'Không tải được dữ liệu.'}</div>`;
            return;
        }

        const emp = data.employee || {};
        const summary = data.summary || {};
        const details = Array.isArray(data.details) ? data.details : [];

        let detailHtml = '';

        details.forEach(item => {
            const isOff = item.status === 'off';
            const weekLabel = formatWeekLabel(item);

            detailHtml += `
                <div class="detail-shift-item">
                    <div class="detail-shift-left">
                        <div class="detail-date-box ${isOff ? 'off' : ''}">
                            <div class="detail-date-day">${item.date || ''}</div>
                            <div class="detail-date-week">${weekLabel}</div>
                        </div>

                        <div class="detail-shift-info">
                            <div class="detail-time-text">${item.time_text || ''}</div>
                            <div class="detail-position-text">${item.position_name || ''}</div>
                        </div>
                    </div>

                    <div class="detail-shift-right">
                        ${getStatusIcon(item.status)}
                    </div>
                </div>
            `;
        });

        modalBody.innerHTML = `
            <div class="detail-header-card">
                <div class="detail-avatar">${emp.initials || ''}</div>
                <div>
                    <div class="detail-emp-name">${emp.full_name || ''}</div>
                    <div class="detail-emp-code">Mã NV: ${emp.employee_code || ''}</div>
                    <div class="detail-emp-pos">Vị trí: ${emp.position_name || ''}</div>
                </div>
            </div>

            <div class="detail-stats">
                <div class="detail-stat-box">
                    <strong>${summary.total_days ?? 0}</strong>
                    <span>Số ngày</span>
                </div>

                <div class="detail-stat-box">
                    <strong>${summary.total_hours ?? 0}h</strong>
                    <span>Tổng giờ</span>
                </div>

                <div class="detail-stat-box">
                    <strong>${summary.status_text || ''}</strong>
                    <span>Trạng thái</span>
                </div>
            </div>

            <div class="detail-section-title">Lịch làm việc tuần này</div>

            <div class="detail-shift-list">
                ${detailHtml || '<div>Không có dữ liệu chi tiết.</div>'}
            </div>
        `;
    } catch (e) {
        console.error('Lỗi load dữ liệu chi tiết:', e);
        modalBody.innerHTML = '<div style="color:red;">Lỗi load dữ liệu</div>';
    }
}

window.addEventListener('click', function (e) {
    const modal = document.getElementById('detailModal');
    if (e.target === modal) {
        closeModal();
    }
});