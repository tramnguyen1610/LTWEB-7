// 1. Các hàm tiện ích
function showToast(msg, bg = '#16A34A') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.style.background = bg;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 3200);
}

function setStep(n) {
    [1, 2, 3].forEach(i => {
        const el = document.getElementById('step' + i);
        if (!el) return;
        el.classList.remove('active', 'done');
        if (i < n) el.classList.add('done');
        if (i === n) el.classList.add('active');
    });
}

// 2. Xử lý UI Chọn file
function onFileSelect(inp) {
    if (inp.files[0]) applyFile(inp.files[0]);
}

function applyFile(f) {
    document.getElementById('uploadArea').classList.remove('vis');
    document.getElementById('fileChosen').classList.add('vis');
    document.getElementById('fileName').textContent = f.name + ' (' + (f.size / 1024).toFixed(1) + ' KB)';

    const m = f.name.match(/(\d{1,2})[-_](\d{4})/);
    if (m) detectedMonth = m[1].padStart(2, '0') + '/' + m[2];
}

function removeFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadArea').classList.add('vis');
    document.getElementById('fileChosen').classList.remove('vis');
}

function resetForm() {
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    document.getElementById('noteInput').value = '';
    document.getElementById('searchInput').value = '';
    removeFile();
    closePreview();
    setStep(1);
}

// 3. GỌI API KIỂM TRA FILE (Kết nối với views.py)
async function runCheck() {
    const from = document.getElementById('dateFrom').value;
    const to = document.getElementById('dateTo').value;
    const file = document.getElementById('fileInput').files[0];

    if (!from) { showToast('⚠️ Vui lòng chọn ngày bắt đầu.', '#D97706'); return; }
    if (!file) { showToast('⚠️ Vui lòng tải lên file Excel/CSV.', '#D97706'); return; }

    const btn = document.getElementById('checkBtn');
    btn.disabled = true;
    btn.classList.add('loading');
    document.getElementById('checkTxt').textContent = 'Đang xử lý...';

    const formData = new FormData();
    formData.append('date_from', from);
    formData.append('date_to', to);
    formData.append('attendance_file', file);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    try {
        const response = await fetch(CHECK_URL, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            employeesData = data.employees;
            detectedMonth = data.month;
            renderPreview();
            setStep(2);
            showToast(`✅ Đọc thành công ${data.total} nhân viên!`, '#16A34A');

            if (data.zero_hours > 0) {
                document.getElementById('warningBox').style.display = 'block';
                document.getElementById('warningText').textContent =
                    `Phát hiện ${data.zero_hours} nhân viên có tổng giờ = 0 trong dữ liệu. Vui lòng kiểm tra trước khi chốt.`;
            } else {
                document.getElementById('warningBox').style.display = 'none';
            }
        } else {
            showToast('❌ ' + (data.error || 'Lỗi xử lý file!'), '#DC2626');
        }
    } catch (error) {
        showToast('❌ Lỗi kết nối server!', '#DC2626');
    } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
        document.getElementById('checkTxt').textContent = '🔍 Kiểm tra dữ liệu';
    }
}

// 4. HIỂN THỊ BẢNG PREVIEW
function renderPreview() {
    const ok = employeesData.filter(r => r.gio > 0).length;
    const zero = employeesData.filter(r => r.gio === 0).length;

    document.getElementById('cTotal').textContent = employeesData.length;
    document.getElementById('cOk').textContent = ok;
    document.getElementById('cZero').textContent = zero;

    const note = document.getElementById('previewNote');
    note.style.color = zero > 0 ? 'var(--warning)' : 'var(--success)';
    note.innerHTML = zero > 0
        ? `⚠️ <strong>${zero}</strong> nhân viên ghi nhận 0 giờ — nên kiểm tra lại trước khi chốt.`
        : `✅ Tất cả nhân viên đều có giờ công. Sẵn sàng chốt.`;

    drawRows(employeesData);
    document.getElementById('previewSection').classList.add('vis');
    document.getElementById('previewSection').scrollIntoView({behavior: 'smooth', block: 'start'});
}

function drawRows(list) {
    const tbody = document.getElementById('previewBody');
    tbody.innerHTML = '';
    list.forEach((r, i) => {
        const z = r.gio === 0;
        const tr = document.createElement('tr');
        if (z) tr.classList.add('rzero');
        tr.innerHTML = `
            <td style="color:#9CA3AF;font-size:12px">${i + 1}</td>
            <td><strong>${r.ma}</strong></td>
            <td>${r.ten}</td>
            <td>${detectedMonth}</td>
            <td>${z ? '<span class="badge bwrn">⚠ Chưa có công</span>' : '<span class="badge bok">✔ Hợp lệ</span>'}</td>
            <td class="td-hours ${z ? 'hwrn' : 'hok'}">${z ? '0.00 h' : r.gio.toFixed(2) + ' h'}</td>
            <td class="td-action">
                <button type="button" class="eye-btn" onclick="openModal('${r.ma}')" title="Xem chi tiết">👁</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// 5. CHỨC NĂNG TÌM KIẾM & LỌC
function setFilter(f) {
    activeFilter = f;
    document.getElementById('btnAll').className = 'fbtn' + (f === 'all' ? ' fa' : '');
    document.getElementById('btnZero').className = 'fbtn' + (f === 'zero' ? ' fz' : '');
    filterTable();
}

function filterTable() {
    const q = document.getElementById('searchInput').value.toLowerCase().trim();
    let list = [...employeesData];
    if (activeFilter === 'zero') list = list.filter(r => r.gio === 0);
    if (q) list = list.filter(r => r.ma.includes(q) || r.ten.toLowerCase().includes(q));
    drawRows(list);
}

function closePreview() {
    document.getElementById('previewSection').classList.remove('vis');
    setStep(1);
}

// 6. GỌI API CHỐT DỮ LIỆU (Lưu vào Database)
async function confirmData() {
    const btn = document.querySelector('.btn-success');
    btn.disabled = true;
    btn.innerHTML = 'Đang chốt... <span class="spinner" style="display:inline-block; width:14px; height:14px; margin-left:5px; vertical-align:middle;"></span>';

    const payload = {
        date_from: document.getElementById('dateFrom').value,
        date_to: document.getElementById('dateTo').value,
        note: document.getElementById('noteInput').value,
        employees: employeesData
    };

    try {
        const response = await fetch(CONFIRM_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.success) {
            setStep(3);
            document.getElementById('previewSection').classList.remove('vis');
            showToast(`🎉 ${data.message}`, '#16A34A');
            // Đợi 2 giây rồi reload trang để cập nhật lịch sử
            setTimeout(() => window.location.reload(), 2000);
        } else {
            showToast('❌ ' + (data.error || 'Lỗi khi chốt dữ liệu!'), '#DC2626');
            btn.disabled = false;
            btn.innerHTML = '✅ Chốt chấm công';
        }
    } catch (error) {
        showToast('❌ Lỗi kết nối server!', '#DC2626');
        btn.disabled = false;
        btn.innerHTML = '✅ Chốt chấm công';
    }
}

// 7. MODAL CHI TIẾT NHÂN VIÊN
function openModal(ma) {
    const emp = employeesData.find(e => e.ma === ma);
    if (!emp) return;

    document.getElementById('modalTitle').textContent = `${emp.ten} (${emp.ma})`;
    document.getElementById('modalSub').textContent = `Kỳ công: ${detectedMonth} — Tổng: ${emp.gio.toFixed(2)} giờ`;

    const workedDays = emp.days || [];
    let missingDays = 0;

    workedDays.forEach(d => {
        if (!d.in || !d.out || d.in === 'nan' || d.out === 'nan') missingDays++;
    });

    document.getElementById('modalSummary').innerHTML = `
        <div class="msumcard ok"><div class="mv">${workedDays.length}</div><div class="ml">Ngày có dữ liệu</div></div>
        <div class="msumcard ok"><div class="mv">${emp.gio.toFixed(1)}</div><div class="ml">Tổng giờ công</div></div>
        <div class="msumcard err"><div class="mv">${missingDays}</div><div class="ml">Lỗi Check-in/out</div></div>
    `;

    if (workedDays.length === 0) {
        document.getElementById('modalBody').innerHTML = '<div class="no-data">📭 Nhân viên không có dữ liệu giờ vào/ra trong file.</div>';
    } else {
        let html = '<table class="day-table"><thead><tr><th>Ngày làm</th><th>Giờ vào</th><th>Giờ ra</th><th>Số giờ</th><th>Trạng thái</th></tr></thead><tbody>';

        workedDays.forEach(d => {
            const inTime = (d.in && d.in !== 'nan') ? d.in : '---';
            const outTime = (d.out && d.out !== 'nan') ? d.out : '---';
            let statusText = '<span class="status-text status-missing">Hợp lệ</span>';

            if (inTime === '---' || outTime === '---') {
                statusText = '<span class="status-text status-missing" style="color:var(--danger)">Thiếu dữ liệu</span>';
            }

            html += `<tr>
                <td><div class="day-cell-date">${d.date}</div></td>
                <td class="time-text">${inTime}</td>
                <td class="time-text">${outTime}</td>
                <td class="late-text">${d.hours}</td>
                <td>${statusText}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        document.getElementById('modalBody').innerHTML = html;
    }
    document.getElementById('modalOverlay').classList.add('open');
}

function closeModal(e) { if (e.target === document.getElementById('modalOverlay')) closeModalDirect(); }
function closeModalDirect() { document.getElementById('modalOverlay').classList.remove('open'); }
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModalDirect(); });