from django.shortcuts import render

# 1. View cho trang Xử lý (Nơi sẽ có form upload file Excel)
def xu_ly_cham_cong(request):
    # (Đoạn code đọc file Excel hôm trước mình viết sẽ được thả vào đây)
    return render(request, 'attendance/xu_ly_cham_cong.html')

# 2. View cho trang Chỉnh sửa (Nơi quản lý sửa giờ bằng tay)
def chinh_sua_cham_cong(request):
    return render(request, 'attendance/chinh_sua_cham_cong.html')

# 3. View cho trang Xem (Nơi hiện danh sách ai đi làm, ai nghỉ)
def xem_cham_cong(request):
    return render(request, 'attendance/xem_cham_cong.html')