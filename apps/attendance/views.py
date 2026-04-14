# apps/attendance/views.py
import pandas as pd
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from apps.attendance.models import Attendance, Shift, ShiftInstance
from apps.employees.models import Employee


# ==========================================
# 1. HÀM DÙNG CHUNG
# ==========================================
def get_dynamic_attendance_data():
    """Hàm gom dữ liệu chấm công từ Database biến thành JSON cho JS đọc"""
    attendances = Attendance.objects.select_related('employee', 'shift_instance__shift').all().order_by(
        '-attendance_date')
    data = []

    days_vn = {0: 'T2', 1: 'T3', 2: 'T4', 3: 'T5', 4: 'T6', 5: 'T7', 6: 'CN'}

    for att in attendances:
        in_time = att.check_in_time.strftime('%H:%M') if att.check_in_time else '--:--'
        out_time = att.check_out_time.strftime('%H:%M') if att.check_out_time else '--:--'
        hours = round(att.work_hours, 2) if att.work_hours else 0

        if hours > 0:
            status = 'Đúng giờ'
        else:
            status = 'Vắng mặt'

        data.append({
            'db_id': att.attendance_id,
            'id': f"NV{att.employee.employee_id:03d}",
            'name': att.employee.full_name,
            'day': days_vn[att.attendance_date.weekday()],
            'date': att.attendance_date.strftime('%d/%m/%Y'),
            'in': in_time,
            'out': out_time,
            'hours': f"{hours} giờ",
            'status': status
        })
    return json.dumps(data)


def get_attendance_history():
    """Lấy lịch sử các lần xử lý chấm công"""
    # TODO: Tạo model AttendanceLog để lưu lịch sử thực tế
    history = [
        {"time": datetime.now() - timedelta(days=15),
         "description": "Quản lý A đã chốt thành công 30NV ở kỳ công tháng 01/2026"},
        {"time": datetime.now() - timedelta(days=45),
         "description": "Quản lý A đã chốt thành công 30NV ở kỳ công tháng 12/2025"},
        {"time": datetime.now() - timedelta(days=75),
         "description": "Quản lý A đã chốt thành công 28NV ở kỳ công tháng 11/2025"},
    ]
    return history


def get_month_status(month_str):
    """Kiểm tra trạng thái chấm công của tháng"""
    try:
        month, year = map(int, month_str.split('/'))
        count = Attendance.objects.filter(
            attendance_date__year=year,
            attendance_date__month=month
        ).count()
        return 'done' if count > 0 else 'pending'
    except:
        return 'pending'


# ==========================================
# 2. VIEW GIAO DIỆN CHÍNH
# ==========================================
@login_required
def xu_ly_cham_cong(request):
    """Trang xử lý chấm công - giao diện chính"""
    today = datetime.now()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    current_month = today.strftime("%m/%Y")
    previous_month = (today.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")

    context = {
        'default_from_date': first_day.strftime('%Y-%m-%d'),
        'default_to_date': last_day.strftime('%Y-%m-%d'),
        'current_month': current_month,
        'previous_month': previous_month,
        'period_start': first_day,
        'period_end': last_day,
        'current_month_status': get_month_status(current_month),
        'attendance_history': get_attendance_history(),
        'user': request.user,
    }
    return render(request, 'attendance/xu_ly_cham_cong.html', context)


def chinh_sua_cham_cong(request):
    """Trang chỉnh sửa chấm công"""
    json_data = get_dynamic_attendance_data()
    return render(request, 'attendance/chinh_sua_cham_cong.html', {'attendance_json': json_data})


def xem_cham_cong(request):
    """Trang xem chấm công"""
    json_data = get_dynamic_attendance_data()
    return render(request, 'attendance/xem_cham_cong.html', {'attendance_json': json_data})


# ==========================================
# 3. API ENDPOINTS
# ==========================================

@csrf_protect
@require_http_methods(["POST"])
def attendance_check(request):
    """
    API: Kiểm tra file chấm công
    POST: date_from, date_to, attendance_file
    Returns: JSON với danh sách nhân viên và giờ công
    """
    try:
        tu_ngay_str = request.POST.get('date_from')
        den_ngay_str = request.POST.get('date_to')
        file_upload = request.FILES.get('attendance_file')

        if not tu_ngay_str:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn ngày bắt đầu'}, status=400)

        if not file_upload:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn file chấm công'}, status=400)

        # Xác định tháng/năm
        try:
            thang_nam = datetime.strptime(tu_ngay_str, "%Y-%m-%d").strftime("%m/%Y")
        except:
            thang_nam = datetime.now().strftime("%m/%Y")

        employees_data = []

        # Đọc file Excel/CSV
        try:
            if file_upload.name.endswith('.csv'):
                df = pd.read_csv(file_upload, skiprows=3, encoding='utf-8')
            else:
                df = pd.read_excel(file_upload, skiprows=3)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Lỗi đọc file: {str(e)}'}, status=400)

        # Dictionary để nhóm dữ liệu theo nhân viên
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
                continue  # Bỏ qua dòng lỗi

        employees_data = list(emp_dict.values())

        # Làm tròn tổng giờ
        for emp in employees_data:
            emp["gio"] = round(emp["gio"], 2)

        total = len(employees_data)
        with_hours = len([e for e in employees_data if e["gio"] > 0])
        zero_hours = total - with_hours

        return JsonResponse({
            'success': True,
            'employees': employees_data,
            'month': thang_nam,
            'total': total,
            'with_hours': with_hours,
            'zero_hours': zero_hours
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi server: {str(e)}'}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def attendance_confirm(request):
    """
    API: Xác nhận chốt chấm công và lưu vào database
    POST: JSON {date_from, date_to, note, employees}
    """
    try:
        data = json.loads(request.body)
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        note = data.get('note', '')
        employees = data.get('employees', [])

        if not employees:
            return JsonResponse({'success': False, 'error': 'Không có dữ liệu nhân viên'}, status=400)

        # Xác định tháng/năm
        try:
            thang_nam = datetime.strptime(date_from, "%Y-%m-%d").strftime("%m/%Y")
        except:
            thang_nam = datetime.now().strftime("%m/%Y")

        saved_count = 0
        errors = []

        # Lấy ca mặc định (nếu chưa có thì tạo)
        default_shift, _ = Shift.objects.get_or_create(
            shift_name="Ca mặc định",
            defaults={'start_time': '08:00', 'end_time': '17:00'}
        )

        for emp_data in employees:
            try:
                ma_nv = emp_data.get('ma')
                ten_nv = emp_data.get('ten', '')
                days = emp_data.get('days', [])

                if not ma_nv:
                    continue

                # Tìm hoặc tạo Employee
                try:
                    employee = Employee.objects.get(employee_id=int(ma_nv))
                except Employee.DoesNotExist:
                    employee = Employee.objects.create(
                        employee_id=int(ma_nv),
                        full_name=ten_nv,
                    )
                except ValueError:
                    errors.append(f"Mã NV không hợp lệ: {ma_nv}")
                    continue

                # Lưu chấm công cho từng ngày
                for day_data in days:
                    try:
                        date_str = day_data.get('date')
                        in_time_str = day_data.get('in')
                        out_time_str = day_data.get('out')
                        hours = day_data.get('hours', 0)

                        if not date_str:
                            continue

                        # Parse ngày
                        day, month, year = map(int, date_str.split('/'))
                        work_date = datetime(year, month, day).date()

                        # Parse giờ
                        check_in = datetime.strptime(in_time_str, "%H:%M").time() if in_time_str else None
                        check_out = datetime.strptime(out_time_str, "%H:%M").time() if out_time_str else None

                        # Tạo hoặc lấy ShiftInstance
                        shift_instance, _ = ShiftInstance.objects.get_or_create(
                            work_date=work_date,
                            defaults={'shift': default_shift}
                        )

                        # Tính giờ đi muộn (nếu có ca làm)
                        late_hours = 0
                        if check_in and shift_instance.shift.start_time:
                            scheduled_start = shift_instance.shift.start_time
                            if check_in > scheduled_start:
                                late_hours = (datetime.combine(work_date, check_in) -
                                              datetime.combine(work_date, scheduled_start)).total_seconds() / 3600.0

                        # Lưu Attendance
                        Attendance.objects.update_or_create(
                            employee=employee,
                            attendance_date=work_date,
                            defaults={
                                'shift_instance': shift_instance,
                                'check_in_time': check_in,
                                'check_out_time': check_out,
                                'work_hours': hours,
                                'late_hours': round(late_hours, 2),
                                'status': 'Present' if hours > 0 else 'Absent'
                            }
                        )
                        saved_count += 1

                    except Exception as e:
                        errors.append(f"Lỗi lưu ngày {day_data.get('date', '')}: {str(e)}")
                        continue

            except Exception as e:
                errors.append(f"Lỗi xử lý nhân viên {ma_nv}: {str(e)}")
                continue

        return JsonResponse({
            'success': True,
            'message': f'Đã lưu thành công {saved_count} bản ghi chấm công',
            'month': thang_nam,
            'saved_count': saved_count,
            'errors': errors if errors else None
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi server: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def employee_attendance_detail(request, employee_id):
    """
    API: Lấy chi tiết chấm công của một nhân viên
    GET: ?month=MM/YYYY
    """
    try:
        month_str = request.GET.get('month', '')

        if not month_str:
            return JsonResponse({'success': False, 'error': 'Thiếu tham số month'}, status=400)

        # Parse tháng/năm
        try:
            month, year = map(int, month_str.split('/'))
        except:
            return JsonResponse({'success': False, 'error': 'Định dạng tháng không hợp lệ (MM/YYYY)'}, status=400)

        # Lấy thông tin nhân viên
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Không tìm thấy nhân viên'}, status=404)

        # Lấy dữ liệu chấm công trong tháng
        attendances = Attendance.objects.filter(
            employee=employee,
            attendance_date__year=year,
            attendance_date__month=month
        ).order_by('attendance_date')

        worked_days = attendances.filter(work_hours__gt=0).count()
        late_days = attendances.filter(late_hours__gt=0).count()
        missing_days = attendances.filter(check_out_time__isnull=True).count()
        total_hours = sum(a.work_hours for a in attendances if a.work_hours)

        attendance_list = []
        for att in attendances:
            in_time = att.check_in_time.strftime('%H:%M') if att.check_in_time else None
            out_time = att.check_out_time.strftime('%H:%M') if att.check_out_time else None

            attendance_list.append({
                'date': att.attendance_date.strftime('%d/%m/%Y'),
                'check_in': in_time,
                'check_out': out_time,
                'late_minutes': int(att.late_hours * 60) if att.late_hours else 0,
                'work_hours': att.work_hours,
                'status': att.status
            })

        return JsonResponse({
            'success': True,
            'employee': {
                'id': employee.employee_id,
                'code': f"NV{employee.employee_id:03d}",
                'name': employee.full_name,
                'worked_days': worked_days,
                'late_days': late_days,
                'missing_days': missing_days,
                'total_hours': round(total_hours, 2),
                'attendances': attendance_list
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi server: {str(e)}'}, status=500)


# ==========================================
# 4. API BỔ SUNG (nếu cần)
# ==========================================

@require_http_methods(["POST"])
def update_attendance(request, attendance_id):
    """
    API: Cập nhật một bản ghi chấm công (dùng cho trang chỉnh sửa)
    """
    try:
        data = json.loads(request.body)

        attendance = Attendance.objects.get(attendance_id=attendance_id)

        if 'check_in' in data and data['check_in']:
            attendance.check_in_time = datetime.strptime(data['check_in'], "%H:%M").time()
        if 'check_out' in data and data['check_out']:
            attendance.check_out_time = datetime.strptime(data['check_out'], "%H:%M").time()
        if 'status' in data:
            attendance.status = data['status']

        # Tính lại giờ công
        if attendance.check_in_time and attendance.check_out_time:
            t_in = datetime.combine(attendance.attendance_date, attendance.check_in_time)
            t_out = datetime.combine(attendance.attendance_date, attendance.check_out_time)
            if t_out < t_in:
                t_out = t_out + timedelta(days=1)
            attendance.work_hours = (t_out - t_in).total_seconds() / 3600.0

        attendance.save()

        return JsonResponse({'success': True, 'message': 'Cập nhật thành công'})

    except Attendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy bản ghi'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
def delete_attendance(request, attendance_id):
    """
    API: Xóa một bản ghi chấm công
    """
    try:
        attendance = Attendance.objects.get(attendance_id=attendance_id)
        attendance.delete()
        return JsonResponse({'success': True, 'message': 'Xóa thành công'})
    except Attendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy bản ghi'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)