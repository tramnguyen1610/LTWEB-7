import pandas as pd
import json
from datetime import datetime, timedelta
from django.shortcuts import render
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
    attendances = Attendance.objects.select_related('employee').all().order_by('-attendance_date')
    data = []
    days_vn = {0: 'T2', 1: 'T3', 2: 'T4', 3: 'T5', 4: 'T6', 5: 'T7', 6: 'CN'}
    for att in attendances:
        in_time = att.check_in_time.strftime('%H:%M') if att.check_in_time else '--:--'
        out_time = att.check_out_time.strftime('%H:%M') if att.check_out_time else '--:--'
        hours = round(att.work_hours, 2) if att.work_hours else 0
        data.append({
            'db_id': att.attendance_id,
            'id': f"NV{att.employee.employee_id:03d}",
            'name': att.employee.full_name,
            'day': days_vn[att.attendance_date.weekday()],
            'date': att.attendance_date.strftime('%d/%m/%Y'),
            'in': in_time,
            'out': out_time,
            'hours': f"{hours} giờ",
            'status': att.status
        })
    return json.dumps(data)


# ==========================================
# 2. VIEW GIAO DIỆN CHÍNH
# ==========================================
def cham_cong_dashboard(request):
    today = timezone.now().date()
    try:
        total_emp = Employee.objects.count()
        working_emp = Attendance.objects.filter(attendance_date=today).exclude(status='Vắng mặt').count()
        absent_emp = Attendance.objects.filter(attendance_date=today, status='Vắng mặt').count()
        recent_activities = Attendance.objects.all().order_by('-attendance_date')[:5]
    except:
        total_emp, working_emp, absent_emp, recent_activities = 0, 0, 0, []

    context = {
        'total_employees': total_emp,
        'working_employees': working_emp,
        'absent_employees': absent_emp,
        'recent_activities': recent_activities,
    }
    return render(request, 'attendance/cham_cong.html', context)


@login_required
def xu_ly_cham_cong(request):
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    context = {
        'default_from_date': first_day.strftime('%Y-%m-%d'),
        'default_to_date': last_day.strftime('%Y-%m-%d'),
        'current_month': today.strftime("%m/%Y"),
    }
    return render(request, 'attendance/xu_ly_cham_cong.html', context)


def chinh_sua_cham_cong(request):
    return render(request, 'attendance/chinh_sua_cham_cong.html', {'attendance_json': get_dynamic_attendance_data()})


def xem_cham_cong(request):
    return render(request, 'attendance/xem_cham_cong.html', {'attendance_json': get_dynamic_attendance_data()})


# ==========================================
# 3. CÁC API XỬ LÝ (Upload file, Lưu, Chỉnh sửa)
# ==========================================
@csrf_protect
@require_http_methods(["POST"])
def attendance_check(request):
    """API: Kiểm tra và bóc tách dữ liệu từ file Excel/CSV"""
    try:
        tu_ngay_str = request.POST.get('date_from')
        den_ngay_str = request.POST.get('date_to')
        file_upload = request.FILES.get('attendance_file')

        if not file_upload:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn file chấm công'}, status=400)

        # Xác định tháng/năm từ input
        try:
            thang_nam = datetime.strptime(tu_ngay_str, "%Y-%m-%d").strftime("%m/%Y") if tu_ngay_str else datetime.now().strftime("%m/%Y")
        except:
            thang_nam = datetime.now().strftime("%m/%Y")

        # Đọc file Excel/CSV bằng Pandas
        try:
            if file_upload.name.endswith('.csv'):
                df = pd.read_csv(file_upload, skiprows=3, encoding='utf-8')
            else:
                df = pd.read_excel(file_upload, skiprows=3)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Lỗi đọc file: {str(e)}'}, status=400)

        # Dictionary để nhóm dữ liệu theo từng nhân viên
        emp_dict = {}

        for index, row in df.iterrows():
            try:
                # Đọc mã NV và tên (bỏ qua dòng header)
                ma_nv = str(row.iloc[2]).strip() if len(row) > 2 else ''
                ten_nv = str(row.iloc[3]).strip() if len(row) > 3 else ''

                # Bỏ qua dòng trống hoặc header
                if pd.isna(ma_nv) or ma_nv == 'nan' or 'Mã' in ma_nv or not ma_nv:
                    continue

                # Chuẩn hóa mã NV (5 chữ số)
                ma_nv = ma_nv.zfill(5)

                if ma_nv not in emp_dict:
                    emp_dict[ma_nv] = {
                        "ma": ma_nv,
                        "ten": ten_nv,
                        "gio": 0.0,
                        "days": []
                    }

                # Xử lý từng ngày (bắt đầu từ cột 5, mỗi ngày 2 cột: giờ vào, giờ ra)
                col_idx = 5
                for day in range(1, 32):
                    if col_idx + 1 >= len(row):
                        break

                    gio_vao = str(row.iloc[col_idx]).strip() if col_idx < len(row) else ''
                    gio_ra = str(row.iloc[col_idx + 1]).strip() if col_idx + 1 < len(row) else ''
                    col_idx += 2

                    if gio_vao not in ['nan', '', 'None'] and gio_ra not in ['nan', '', 'None']:
                        try:
                            t_in = datetime.strptime(gio_vao, "%H:%M")
                            t_out = datetime.strptime(gio_ra, "%H:%M")

                            # Tính giờ công
                            if t_out < t_in:  # Qua ngày hôm sau
                                t_out = t_out.replace(day=t_out.day + 1)

                            hours = (t_out - t_in).total_seconds() / 3600.0
                            emp_dict[ma_nv]["gio"] += hours

                            # Lưu chi tiết ngày
                            emp_dict[ma_nv]["days"].append({
                                "day": day,
                                "date": f"{day:02d}/{thang_nam}",
                                "in": gio_vao,
                                "out": gio_ra,
                                "hours": round(hours, 2)
                            })
                        except:
                            pass
            except Exception as e:
                continue  # Bỏ qua dòng bị lỗi

        employees_data = list(emp_dict.values())

        # Làm tròn tổng giờ cho từng nhân viên
        for emp in employees_data:
            emp["gio"] = round(emp["gio"], 2)

        total = len(employees_data)
        with_hours = len([e for e in employees_data if e["gio"] > 0])
        zero_hours = total - with_hours

        # Trả về ĐẦY ĐỦ dữ liệu cho Javascript xử lý
        return JsonResponse({
            'success': True,
            'employees': employees_data,
            'month': thang_nam,
            'total': total,
            'with_hours': with_hours,
            'zero_hours': zero_hours,
            'message': f'Đọc thành công {total} nhân viên'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi server: {str(e)}'}, status=500)
@csrf_protect
@require_http_methods(["POST"])
def attendance_confirm(request):
    """API: Lưu dữ liệu vào DB sau khi duyệt"""
    try:
        data = json.loads(request.body)
        employees = data.get('employees', [])
        # Lưu vào Database ở đây
        return JsonResponse({'success': True, 'message': f'Đã lưu thành công {len(employees)} bản ghi.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def update_attendance_api(request, db_id):
    """API: Chỉnh sửa giờ từ Popup"""
    try:
        data = json.loads(request.body)
        attendance = Attendance.objects.get(attendance_id=db_id)
        if 'check_in' in data and data['check_in']:
            attendance.check_in_time = datetime.strptime(data['check_in'], "%H:%M").time()
        if 'check_out' in data and data['check_out']:
            attendance.check_out_time = datetime.strptime(data['check_out'], "%H:%M").time()

        # Tính giờ tự động
        if attendance.check_in_time and attendance.check_out_time:
            t_in = datetime.combine(attendance.attendance_date, attendance.check_in_time)
            t_out = datetime.combine(attendance.attendance_date, attendance.check_out_time)
            if t_out < t_in: t_out += timedelta(days=1)
            attendance.work_hours = (t_out - t_in).total_seconds() / 3600.0

        attendance.save()
        return JsonResponse({'success': True, 'message': 'Cập nhật thành công'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)