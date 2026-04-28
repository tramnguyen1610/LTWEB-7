// =========================
// 1. CSRF TOKEN
// =========================
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

// =========================
// 2. BIẾN DÙNG CHUNG
// =========================
const realToday = new Date();
realToday.setHours(0, 0, 0, 0);

// Tìm thứ 2 tuần hiện tại
const currentDay = realToday.getDay();
const distToMon = currentDay === 0 ? -6 : 1 - currentDay;
const currentWeekStart = new Date(realToday);
currentWeekStart.setDate(realToday.getDate() + distToMon);
currentWeekStart.setHours(0, 0, 0, 0);

// Chỉ cho xếp từ thứ 2 tuần sau
const nextWeekStart = new Date(currentWeekStart);
nextWeekStart.setDate(currentWeekStart.getDate() + 7);
nextWeekStart.setHours(0, 0, 0, 0);

// Mặc định load tuần sau
let selectedDate = new Date(nextWeekStart);
let currentYear = selectedDate.getFullYear();
let currentMonth = selectedDate.getMonth();

let weekStart, weekEnd;
const caKeys = ['sang', 'chieu', 'toi'];
const caLabels = {
    sang: 'Ca Sáng',
    chieu: 'Ca Chiều',
    toi: 'Ca Tối'
};

let positions = [];
let schedule = {};

// =========================
// 3. HÀM PHỤ
// =========================
function formatDateKey(date) {
    const d = new Date(date);
    const offset = d.getTimezoneOffset() * 60000;
    return new Date(d.getTime() - offset).toISOString().split('T')[0];
}

function getVietnameseDayName(date) {
    const days = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
    return days[date.getDay()];
}

function pad2(num) {
    return String(num).padStart(2, '0');
}

function calculateWeekRange(date) {
    const d = new Date(date);
    const day = d.getDay();
    const distanceToMonday = day === 0 ? -6 : 1 - day;

    weekStart = new Date(d);
    weekStart.setDate(d.getDate() + distanceToMonday);
    weekStart.setHours(0, 0, 0, 0);

    weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    weekEnd.setHours(23, 59, 59, 999);
}

function updateSetupTitle() {
    const title = document.getElementById('setupTitle');
    if (!title) return;

    title.textContent = `Thiết lập nhân sự - ${getVietnameseDayName(selectedDate)}, ${pad2(selectedDate.getDate())}/${pad2(selectedDate.getMonth() + 1)}`;
}

// =========================
// 4. GỌI API LẤY DỮ LIỆU
// =========================
async function fetchScheduleData() {
    calculateWeekRange(selectedDate);

    const startStr = formatDateKey(weekStart);
    const endStr = formatDateKey(weekEnd);

    try {
        const response = await fetch(`${API_CAPACITY_URL}?start_date=${startStr}&end_date=${endStr}`);
        const result = await response.json();

        if (result.status === 'success') {
            schedule = result.data || {};

            const firstDateData = Object.values(schedule)[0];
            if (firstDateData && firstDateData.sang) {
                positions = Object.keys(firstDateData.sang);
            } else {
                positions = [];
            }

            renderCalendar();
            updateSetupTitle();
            renderPosList();
            renderOverviewTable();
        } else {
            console.error("API trả lỗi:", result.message);
            alert(result.message || "Không lấy được dữ liệu lịch.");
        }
    } catch (error) {
        console.error("Lỗi khi lấy dữ liệu:", error);
        alert("Không thể tải dữ liệu lịch.");
    }
}

// =========================
// 5. LƯU LỊCH
// =========================
async function saveScheduleToBackend() {
    console.log("Đang bắt đầu quá trình lưu...");

    const btn = document.querySelector('.btn-luu');
    const toast = document.getElementById('toast');

    if (btn) {
        btn.disabled = true;
        btn.textContent = "Đang lưu...";
        btn.style.opacity = "0.7";
    }

    try {
        const response = await fetch(API_CAPACITY_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                schedule: schedule
            })
        });

        const result = await response.json();
        console.log("Phản hồi từ server:", result);

        if (result.status === 'success') {
            if (toast) {
                toast.textContent = "✅ " + result.message;
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            } else {
                alert(result.message || "Lưu lịch thành công");
            }
        } else {
            alert("Lỗi từ server: " + (result.message || "Không xác định"));
        }
    } catch (error) {
        console.error("Lỗi khi gọi API:", error);
        alert("Không thể kết nối tới server hoặc backend đang lỗi.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Lưu lịch";
            btn.style.opacity = "1";
        }
    }
}

// =========================
// 6. VẼ CALENDAR
// =========================
function renderCalendar() {
    const grid = document.getElementById('calGrid');
    const monthLabel = document.getElementById('calMonthLabel');

    if (!grid || !monthLabel) return;

    grid.innerHTML = '';
    monthLabel.textContent = `Tháng ${currentMonth + 1}/${currentYear}`;

    ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'].forEach(h => {
        const el = document.createElement('div');
        el.className = 'cal-day-name';
        el.textContent = h;
        grid.appendChild(el);
    });

    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
    const emptyDays = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1;

    for (let i = 0; i < emptyDays; i++) {
        const el = document.createElement('div');
        grid.appendChild(el);
    }

    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    for (let d = 1; d <= daysInMonth; d++) {
        const dayDate = new Date(currentYear, currentMonth, d);
        dayDate.setHours(0, 0, 0, 0);

        const el = document.createElement('div');
        el.className = 'cal-day';
        el.textContent = d;

        const ws = new Date(weekStart).setHours(0, 0, 0, 0);
        const we = new Date(weekEnd).setHours(0, 0, 0, 0);
        const sd = new Date(selectedDate).setHours(0, 0, 0, 0);

        const inSelectedWeek = dayDate.getTime() >= ws && dayDate.getTime() <= we;
        const isCurrentSelected = dayDate.getTime() === sd;
        const isToday = dayDate.getTime() === realToday.getTime();
        const isClickable = dayDate.getTime() >= nextWeekStart.getTime();

        if (inSelectedWeek && isClickable) {
            el.classList.add('selected-week');
        }

        if (isToday) {
            el.style.border = "1px solid #8B1A2B";
        }

        if (isCurrentSelected && isClickable) {
            el.classList.remove('selected-week');
            el.classList.add('today');
        }

        if (isClickable) {
            el.style.cursor = 'pointer';
            el.onclick = function () {
                selectedDate = new Date(currentYear, currentMonth, d);

                const clickedWeekStart = new Date(selectedDate);
                const clickedDay = clickedWeekStart.getDay();
                const distanceToMonday = clickedDay === 0 ? -6 : 1 - clickedDay;
                clickedWeekStart.setDate(clickedWeekStart.getDate() + distanceToMonday);
                clickedWeekStart.setHours(0, 0, 0, 0);

                const currentRenderedWeekStart = new Date(weekStart);
                currentRenderedWeekStart.setHours(0, 0, 0, 0);

                if (clickedWeekStart.getTime() !== currentRenderedWeekStart.getTime()) {
                    currentYear = selectedDate.getFullYear();
                    currentMonth = selectedDate.getMonth();
                    fetchScheduleData();
                } else {
                    updateSetupTitle();
                    renderCalendar();
                    renderPosList();
                }
            };
        } else {
            el.style.opacity = '0.25';
            el.style.cursor = 'not-allowed';
            el.style.backgroundColor = 'transparent';
        }

        grid.appendChild(el);
    }
}

// =========================
// 7. DANH SÁCH VỊ TRÍ
// =========================
function renderPosList() {
    const caSelect = document.getElementById('caSelect');
    const container = document.getElementById('posList');

    if (!caSelect || !container) return;

    const ca = caSelect.value;
    const ds = formatDateKey(selectedDate);

    container.innerHTML = '';

    if (!schedule[ds] || !schedule[ds][ca]) return;

    positions.forEach(pos => {
        const val = schedule[ds][ca][pos] || 0;

        const row = document.createElement('div');
        row.className = 'pos-row';
        row.innerHTML = `
            <span>${pos}</span>
            <div class="qty-control">
                <button type="button" class="qty-btn" onclick="changeQty('${ca}','${pos}',-1)">—</button>
                <span class="qty-val">${val}</span>
                <button type="button" class="qty-btn" onclick="changeQty('${ca}','${pos}',1)">+</button>
            </div>
        `;
        container.appendChild(row);
    });
}

// =========================
// 8. TĂNG/GIẢM SỐ LƯỢNG
// =========================
function changeQty(ca, pos, delta) {
    const ds = formatDateKey(selectedDate);

    if (!schedule[ds] || !schedule[ds][ca] || schedule[ds][ca][pos] === undefined) {
        return;
    }

    schedule[ds][ca][pos] = Math.max(0, schedule[ds][ca][pos] + delta);

    const applyAll = document.getElementById('applyAll');
    if (applyAll && applyAll.checked) {
        for (let i = 0; i < 7; i++) {
            const dDate = new Date(weekStart);
            dDate.setDate(dDate.getDate() + i);
            const d = formatDateKey(dDate);

            if (schedule[d] && schedule[d][ca] && schedule[d][ca][pos] !== undefined) {
                schedule[d][ca][pos] = schedule[ds][ca][pos];
            }
        }
    }

    renderPosList();
    renderOverviewTable();
}

// =========================
// 9. BẢNG TỔNG QUAN
// =========================
function renderOverviewTable() {
    const table = document.getElementById('ovTable');
    if (!table) return;

    if (Object.keys(schedule).length === 0 || positions.length === 0) {
        table.innerHTML = '';
        return;
    }

    let daysHtml = '';
    for (let i = 0; i < 7; i++) {
        const dDate = new Date(weekStart);
        dDate.setDate(dDate.getDate() + i);
        daysHtml += `<th>${getVietnameseDayName(dDate)} ${pad2(dDate.getDate())}/${pad2(dDate.getMonth() + 1)}</th>`;
    }

    let html = `<thead><tr><th>CA LÀM</th><th>VỊ TRÍ</th>${daysHtml}</tr></thead><tbody>`;

    caKeys.forEach(ca => {
        positions.forEach((pos, pi) => {
            html += `<tr>
                ${pi === 0 ? `<td rowspan="${positions.length}" class="${ca === 'sang' ? 'ca-sang' : ca === 'chieu' ? 'ca-chieu' : 'ca-toi'}">${caLabels[ca]}</td>` : ''}
                <td style="font-weight:600;">${pos}</td>`;

            for (let i = 0; i < 7; i++) {
                const dDate = new Date(weekStart);
                dDate.setDate(dDate.getDate() + i);
                const ds = formatDateKey(dDate);
                const val = schedule[ds] && schedule[ds][ca] ? (schedule[ds][ca][pos] || 0) : 0;
                html += `<td>${val}</td>`;
            }

            html += `</tr>`;
        });
    });

    html += `</tbody>`;
    table.innerHTML = html;
}

// =========================
// 10. TẢI LẠI DỮ LIỆU
// =========================
function handleHuy() {
    if (confirm('Tải lại dữ liệu ban đầu?')) {
        fetchScheduleData();
    }
}

// =========================
// 11. ĐỔI THÁNG
// =========================
function changeMonth(step) {
    currentMonth += step;

    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }

    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }

    renderCalendar();
}

// =========================
// 12. KHI TRANG LOAD
// =========================
document.addEventListener('DOMContentLoaded', () => {
    fetchScheduleData();

    const userMenuBtn = document.getElementById('userMenuBtn');
    const logoutDropdown = document.getElementById('logoutDropdown');
    const caSelect = document.getElementById('caSelect');

    if (caSelect) {
        caSelect.addEventListener('change', renderPosList);
    }

    if (userMenuBtn && logoutDropdown) {
        userMenuBtn.addEventListener('click', function (e) {
            logoutDropdown.classList.toggle('show');
            e.stopPropagation();
        });

        document.addEventListener('click', function (e) {
            if (!userMenuBtn.contains(e.target)) {
                logoutDropdown.classList.remove('show');
            }
        });
    }
});