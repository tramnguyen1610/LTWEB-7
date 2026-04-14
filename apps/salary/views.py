from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from .models import Payroll, SalaryLevel
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from .logic import calculate_payroll_data
from decimal import Decimal


# --- PHẦN 1: XEM VÀ THIẾT LẬP (ĐÃ CÓ) ---

def xem_thong_tin_luong(request):
    """View hiển thị danh sách lương ra màn hình"""
    payrolls = Payroll.objects.select_related('employee').all().order_by('-payroll_period')
    context = {'payrolls': payrolls}
    return render(request, 'salary/xem_thong_tin_luong.html', context)


def thiet_lap_muc_luong(request):
    """View hiển thị danh sách các mức lương theo vị trí"""
    salary_levels = SalaryLevel.objects.select_related('position').all().order_by('position__position_name')
    return render(request, 'salary/thiet_lap_muc_luong.html', {'salary_levels': salary_levels})


def cap_nhat_muc_luong(request):
    """Hàm xử lý cập nhật lương từ Popup"""
    if request.method == 'POST':
        level_id = request.POST.get('level_id')
        new_salary = request.POST.get('new_salary')
        if level_id and new_salary:
            sl = get_object_or_404(SalaryLevel, pk=level_id)
            sl.base_salary = new_salary
            sl.save()
    return redirect('salary:thiet_lap_muc_luong')


# --- PHẦN 2: TÍNH LƯƠNG (MỚI THÊM) ---

def tinh_luong(request):
    """Hiển thị giao diện trang tính lương"""
    return render(request, 'salary/tinh_luong.html')


def api_preview_tinh_luong(request):
    """API trả về dữ liệu xem trước: Tổng NV, Tổng giờ, Dự kiến tiền (Trừ Quản lý)"""
    period = request.GET.get('period')  # Định dạng 'MM-YYYY'
    if not period:
        return JsonResponse({'error': 'Thiếu kỳ lương'}, status=400)

    try:
        month, year = map(int, period.split('-'))

        # 1. Lọc nhân viên có đi làm trong tháng (Trừ Quản lý)
        # Sử dụng __icontains để lọc không phân biệt hoa thường chữ 'Quản lý'
        employees = Employee.objects.filter(
            attendance__attendance_date__month=month,
            attendance__attendance_date__year=year
        ).exclude(position__position_name__icontains="Quản lý").distinct()

        total_employees = employees.count()

        # 2. Tổng giờ làm của nhân viên (Trừ Quản lý)
        total_hours = Attendance.objects.filter(
            attendance_date__month=month,
            attendance_date__year=year
        ).exclude(employee__position__position_name__icontains="Quản lý").aggregate(
            Sum('work_hours'))['work_hours__sum'] or 0

        # 3. Dự kiến tổng tiền lương (Dùng hàm logic.py)
        total_estimated = 0
        for emp in employees:
            data = calculate_payroll_data(emp, period)
            total_estimated += data['total_salary']

        return JsonResponse({
            'total_employees': total_employees,
            'total_hours': round(float(total_hours), 1),
            'total_estimated': float(total_estimated),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_thuc_hien_tinh_luong(request):
    """Lưu bảng lương vào Database khi nhấn nút Bắt đầu tính"""
    if request.method == 'POST':
        period = request.POST.get('period')
        if not period:
            return JsonResponse({'status': 'error', 'message': 'Thiếu kỳ lương'}, status=400)

        month, year = map(int, period.split('-'))

        # Lấy danh sách nhân viên hợp lệ
        employees = Employee.objects.filter(
            attendance__attendance_date__month=month,
            attendance__attendance_date__year=year
        ).exclude(position__position_name__icontains="Quản lý").distinct()

        count = 0
        for emp in employees:
            # Nếu đã tính lương tháng này rồi thì xóa đi để ghi đè dữ liệu mới nhất
            Payroll.objects.filter(employee=emp, payroll_period=period).delete()

            # Tạo mới (Hàm save() trong models.py của Sương sẽ tự gọi logic.py để tính số tiền)
            Payroll.objects.create(employee=emp, payroll_period=period)
            count += 1

        return JsonResponse({
            'status': 'success',
            'message': f'Đã tính và lưu bảng lương thành công cho {count} nhân viên.'
        })
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=400)
def ket_qua_tinh_luong(request):
    period = request.GET.get('period')
    if not period:
        return redirect('salary:tinh_luong')
    try:
        month, year = map(int, period.split('-'))
    except:
        return redirect('salary:tinh_luong')

    # Lấy danh sách nhân viên có chấm công trong tháng (trừ quản lý)
    employees = Employee.objects.filter(
        attendance__attendance_date__month=month,
        attendance__attendance_date__year=year
    ).exclude(position__position_name__icontains="Quản lý").distinct()

    data = []
    total_salary_sum = 0
    for emp in employees:
        # Tính tổng giờ làm
        total_hours = Attendance.objects.filter(
            employee=emp,
            attendance_date__month=month,
            attendance_date__year=year
        ).aggregate(Sum('work_hours'))['work_hours__sum'] or 0

        salary_lv = emp.salary_level
        if salary_lv:
            if salary_lv.pay_type == 'MONTHLY':
                base_salary = salary_lv.base_salary
                # Lương cơ bản = base_salary (không phụ thuộc giờ)
                total_salary = base_salary
                hourly_rate_display = f"{base_salary:,.0f}đ/tháng"
            else:
                hourly_rate = salary_lv.base_salary
                total_salary = hourly_rate * Decimal(str(total_hours))
                hourly_rate_display = f"{hourly_rate:,.0f}đ/giờ"
        else:
            total_salary = 0
            hourly_rate_display = "Chưa có mức lương"

        total_salary_sum += total_salary

        data.append({
            'employee_id': emp.employee_id,
            'full_name': emp.full_name,
            'position_name': emp.position.position_name,
            'hourly_rate_display': hourly_rate_display,
            'work_hours': total_hours,
            'total_salary': total_salary,
        })

    context = {
        'period': period,
        'data': data,
        'total_sum': total_salary_sum,
    }
    return render(request, 'salary/ket_qua_tinh_luong.html', context)

def api_luu_bang_luong(request):
    if request.method == 'POST':
        period = request.POST.get('period')
        if not period:
            return JsonResponse({'status': 'error', 'message': 'Thiếu kỳ lương'}, status=400)
        try:
            month, year = map(int, period.split('-'))
        except:
            return JsonResponse({'status': 'error', 'message': 'Kỳ lương không hợp lệ'}, status=400)

        employees = Employee.objects.filter(
            attendance__attendance_date__month=month,
            attendance__attendance_date__year=year
        ).exclude(position__position_name__icontains="Quản lý").distinct()

        count = 0
        for emp in employees:
            # Xóa cũ nếu có
            Payroll.objects.filter(employee=emp, payroll_period=period).delete()
            # Tạo mới (save sẽ tự tính)
            Payroll.objects.create(employee=emp, payroll_period=period)
            count += 1

        return JsonResponse({'status': 'success', 'message': f'Đã lưu bảng lương cho {count} nhân viên.'})
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=400)


def api_danh_sach_luong(request):
    """API trả về danh sách lương chi tiết của tháng cho giao diện Xem thông tin lương"""
    period = request.GET.get('period')  # Định dạng 'MM-YYYY'
    if not period:
        return JsonResponse({'data': []})

    try:
        month, year = map(int, period.split('-'))

        # Lấy danh sách bảng lương đã tính trong tháng
        payrolls = Payroll.objects.filter(
            payroll_period=period
        ).select_related('employee', 'employee__position', 'employee__salary_level')

        data = []
        for p in payrolls:
            emp = p.employee

            # Tính tổng giờ làm thực tế từ bảng Attendance
            hours = Attendance.objects.filter(
                employee=emp,
                attendance_date__month=month,
                attendance_date__year=year
            ).aggregate(Sum('work_hours'))['work_hours__sum'] or 0

            # Lấy thông tin mức lương
            rate = emp.salary_level.base_salary if emp.salary_level else 0
            level_name = emp.salary_level.level_name if emp.salary_level else "Chưa thiết lập"

            # Công thức tính toán
            base_salary = float(rate) * float(hours)
            bonus = float(p.total_bonus)
            penalty = float(p.total_penalty)
            total_salary = base_salary + bonus - penalty

            # Gói dữ liệu
            data.append({
                'id': f"NV{emp.employee_id:03d}",
                'name': emp.full_name,
                'role': emp.position.position_name,
                'level_name': level_name,  # Thêm Level Name cho Modal
                'rate': float(rate),
                'hours': float(hours),
                'base_salary': base_salary,
                'bonus': bonus,
                'penalty': penalty,
                'total_salary': total_salary,
                # Dùng UI Avatars tạo ảnh đại diện tự động từ tên nhân viên
                'avatar': f'https://ui-avatars.com/api/?name={emp.full_name}&background=8B1A2B&color=fff'
            })

        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)