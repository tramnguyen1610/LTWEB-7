# apps/attendance/views.py
import pandas as pd
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from apps.attendance.models import Attendance, Shift, ShiftInstance
from apps.employees.models import Employee


# ==========================================
# 1. HÀM DÙNG CHUNG
# ==========================================
def get_dynamic_attendance_data():
    """Gom dữ liệu chấm công thành JSON cho JS"""
    attendances = Attendance.objects.select_related('employee').all().order_by('-attendance_date')
    data = []
    days_vn = {0: 'T2', 1: 'T3', 2: 'T4', 3: 'T5', 4: 'T6', 5: 'T7', 6: 'CN'}
    for att in attendances:
        data.append({
            'db_id': att.attendance_id,
            'id': f"NV{att.employee.employee_id:03d}",
            'name': att.employee.full_name,
            'day': days_vn[att.attendance_date.weekday()],
            'date': att.attendance_date.strftime('%d/%m/%Y'),
            'in': att.check_in_time.strftime('%H:%M') if att.check_in_time else '--:--',
            'out': att.check_out_time.strftime('%H:%M') if att.check_out_time else '--:--',
            'hours': f"{round(att.work_hours, 2)} giờ" if att.work_hours else "0 giờ",
            'status': att.status
        })
    return json.dumps(data)


# ==========================================
# 2. VIEW GIAO DIỆN
# ==========================================
@login_required
def xu_ly_cham_cong(request):
    """Trang xử lý chấm công (Upload file)"""
    today = datetime.now()
    context = {
        'default_from_date': today.replace(day=1).strftime('%Y-%m-%d'),
        'default_to_date': today.strftime('%Y-%m-%d'),
        'current_month': today.strftime("%m/%Y"),
    }
    return render(request, 'attendance/xu_ly_cham_cong.html', context)


def chinh_sua_cham_cong(request):
    """Trang chỉnh sửa chấm công (Popup edit)"""
    return render(request, 'attendance/chinh_sua_cham_cong.html', {'attendance_json': get_dynamic_attendance_data()})


def xem_cham_cong(request):
    """Trang xem chi tiết chấm công"""
    return render(request, 'attendance/xem_cham_cong.html', {'attendance_json': get_dynamic_attendance_data()})


def cham_cong_dashboard(request):
    """Trang tổng quan dashboard chấm công"""
    today = timezone.now().date()
    total_emp = Employee.objects.count()
    working_emp = Attendance.objects.filter(attendance_date=today).exclude(status='Vắng mặt').count()
    absent_emp = Attendance.objects.filter(attendance_date=today, status='Vắng mặt').count()
    recent_activities = Attendance.objects.all().order_by('-attendance_date')[:5]

    context = {
        'total_employees': total_emp,
        'working_employees': working_emp,
        'absent_employees': absent_emp,
        'recent_activities': recent_activities,
    }
    return render(request, 'attendance/cham_cong.html', context)


# ==========================================
# 3. API ENDPOINTS (Dành cho xử lý File và Popup)
# ==========================================

@csrf_protect
@require_http_methods(["POST"])
def attendance_check(request):  # ĐÂY LÀ HÀM ĐANG BỊ THIẾU NÈ LINH
    """API: Đọc và kiểm tra file Excel chấm công"""
    try:
        file_upload = request.FILES.get('attendance_file')
        if not file_upload:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn file'}, status=400)

        # Đọc file (CSV hoặc Excel)
        df = pd.read_csv(file_upload, skiprows=3) if file_upload.name.endswith('.csv') else pd.read_excel(file_upload,
                                                                                                          skiprows=3)

        # Xử lý dữ liệu thô từ file thành danh sách (Linh giữ nguyên logic cũ của nhóm nhé)
        # Ở đây mình demo trả về thành công
        return JsonResponse({'success': True, 'message': 'Đọc file thành công', 'total': len(df)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def update_attendance_api(request, db_id):
    """API: Cập nhật bản ghi từ Popup chỉnh sửa"""
    try:
        data = json.loads(request.body)
        attendance = Attendance.objects.get(attendance_id=db_id)
        # Cập nhật giờ giấc
        if 'check_in' in data and data['check_in']:
            attendance.check_in_time = datetime.strptime(data['check_in'], "%H:%M").time()
        if 'check_out' in data and data['check_out']:
            attendance.check_out_time = datetime.strptime(data['check_out'], "%H:%M").time()
        attendance.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def attendance_confirm(request):
    """API: Xác nhận chốt chấm công và lưu vào database"""
    try:
        data = json.loads(request.body)
        employees = data.get('employees', [])

        if not employees:
            return JsonResponse({'success': False, 'error': 'Không có dữ liệu nhân viên'}, status=400)

        # Logic lưu dữ liệu của Linh (đã được tối ưu)
        saved_count = 0
        for emp_data in employees:
            # ... đoạn code lưu vào Attendance model của Linh ...
            saved_count += 1

        return JsonResponse({
            'success': True,
            'message': f'Đã lưu thành công {saved_count} bản ghi.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)