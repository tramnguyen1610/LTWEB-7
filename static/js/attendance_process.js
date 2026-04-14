// static/js/attendance_process.js

function renderTable(data) {
    const tbody = document.getElementById('previewBody');
    tbody.innerHTML = '';

    data.forEach(emp => {
        const isZero = emp.gio === 0;
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td><strong>${emp.ma}</strong></td>
            <td>${emp.ten}</td>
            <td style="font-weight: bold; color: ${isZero ? 'red' : 'green'}">${emp.gio.toFixed(2)} h</td>
            <td>
                <span class="badge ${isZero ? 'bwrn' : 'bok'}">
                    ${isZero ? '⚠️ 0 Giờ' : '✔ Hợp lệ'}
                </span>
            </td>
            <td><button onclick="alert('Xem chi tiết nhân viên ${emp.ma}')">👁 Xem</button></td>
        `;
        tbody.appendChild(tr);
    });
}