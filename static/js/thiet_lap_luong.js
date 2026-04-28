// Hàm mở Modal và đổ dữ liệu
// Hàm mở Modal và đổ dữ liệu
function openModal(id, positionName, levelName, currentSalary, payTypeUnit) {
    document.getElementById('modal_level_id').value = id;

    // Đã sửa lại dòng này: Chỉ hiển thị levelName thôi để không bị lặp chữ
    document.getElementById('modal_level_desc').innerText = levelName;

    // Xóa dấu phẩy, chấm để nhét vào ô input type="number"
    let cleanSalary = currentSalary.replace(/,/g, '').replace(/\./g, '');
    document.getElementById('modal_new_salary').value = cleanSalary;

    document.getElementById('modal_salary_label').innerText = "Mức lương mới (VND " + payTypeUnit + ")";

    // Thêm class 'show' để hiển thị Popup
    document.getElementById('salaryModal').classList.add('show');
}
// Hàm đóng Modal
function closeModal() {
    // Xóa class 'show' để ẩn Popup
    document.getElementById('salaryModal').classList.remove('show');
}