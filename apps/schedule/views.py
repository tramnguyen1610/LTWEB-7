import json
import calendar
from datetime import datetime, timedelta, date

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ScheduleRegistration, ScheduleCapacity
from apps.attendance.models import ShiftInstance, Shift
from apps.employees.models import Position

from django.views.decorators.http import require_GET, require_POST

def schedule_register(request):
    if request.method == "POST":
        pass
    shifts = ShiftInstance.objects.all()
    return render(request, 'schedule/dangkylichlam.html', {'shifts': shifts})


def schedule_approve(request):
    registrations = ScheduleRegistration.objects.filter(approval_status='PENDING')
    return render(request, 'schedule/duyetlichlamviec.html', {'registrations': registrations})


def lichlam(request):
    name = request.GET.get('name', '').strip()
    month_year = request.GET.get('month_year', '').strip()
    week = request.GET.get('week', '').strip()

    registrations = ScheduleRegistration.objects.select_related(
        'employee',
        'shift_instance',
        'shift_instance__shift'
    ).all()

    if name:
        registrations = registrations.filter(
            employee__full_name__icontains=name
        )

    selected_year = None
    selected_month = None

    if month_year:
        try:
            selected_year, selected_month = map(int, month_year.split('-'))
            registrations = registrations.filter(
                shift_instance__work_date__year=selected_year,
                shift_instance__work_date__month=selected_month
            )
        except ValueError:
            pass

    if selected_year and selected_month and week:
        try:
            week_num = int(week)
            month_matrix = calendar.monthcalendar(selected_year, selected_month)

            if 1 <= week_num <= len(month_matrix):
                valid_days = [d for d in month_matrix[week_num - 1] if d != 0]
                registrations = registrations.filter(
                    shift_instance__work_date__day__in=valid_days
                )
        except ValueError:
            pass

    employee_map = {}

    for reg in registrations:
        emp = reg.employee
        emp_id = emp.employee_id

        if emp_id not in employee_map:
            employee_map[emp_id] = {
                'id': emp_id,
                'employee_code': f'NV{str(emp_id).zfill(3)}',
                'employee_name': emp.full_name,
                'total_days_set': set(),
                'total_hours': 0,
                'created_at': reg.registration_date,
                'approval_status': reg.approval_status,
            }

        employee_map[emp_id]['total_days_set'].add(reg.shift_instance.work_date)
        employee_map[emp_id]['total_hours'] += 5

        if reg.registration_date > employee_map[emp_id]['created_at']:
            employee_map[emp_id]['created_at'] = reg.registration_date

        priority = {'PENDING': 3, 'REJECTED': 2, 'APPROVED': 1}
        old_status = employee_map[emp_id]['approval_status']
        new_status = reg.approval_status

        if priority.get(new_status, 0) > priority.get(old_status, 0):
            employee_map[emp_id]['approval_status'] = new_status

    schedules = []
    for emp_data in employee_map.values():
        status = emp_data['approval_status']

        if status == 'APPROVED':
            status_class = 'approved'
            status_display = 'Đã duyệt'
        elif status == 'PENDING':
            status_class = 'pending'
            status_display = 'Chờ duyệt'
        else:
            status_class = 'rejected'
            status_display = 'Từ chối'

        schedules.append({
            'id': emp_data['id'],
            'employee_code': emp_data['employee_code'],
            'employee_name': emp_data['employee_name'],
            'total_days': len(emp_data['total_days_set']),
            'total_hours': emp_data['total_hours'],
            'created_at': emp_data['created_at'],
            'status_class': status_class,
            'status_display': status_display,
        })

    schedules.sort(key=lambda x: x['employee_code'])

    today = date.today()
    months_list = []
    for i in range(1, 13):
        months_list.append({
            'value': f"{today.year}-{i:02d}",
            'label': f"Tháng {i}/{today.year}"
        })

    approved_count = sum(1 for s in schedules if s['status_class'] == 'approved')
    pending_count = sum(1 for s in schedules if s['status_class'] == 'pending')
    rejected_count = sum(1 for s in schedules if s['status_class'] == 'rejected')

    context = {
        'schedules': schedules,
        'total_count': len(schedules),
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'months_list': months_list,
        'selected_month_year': month_year,
        'selected_week': str(week) if week else '',
        'search_name': name,
        'url_name': 'xemlichlamviec',
    }

    return render(request, 'schedule/xemlichlamviec.html', context)


def api_schedule_detail(request, employee_id):
    month_year = request.GET.get('month_year', '').strip()
    week = request.GET.get('week', '').strip()

    registrations = ScheduleRegistration.objects.select_related(
        'employee',
        'shift_instance',
        'shift_instance__shift'
    ).filter(employee__employee_id=employee_id).order_by('shift_instance__work_date')

    selected_year = None
    selected_month = None
    selected_week_dates = []

    if month_year:
        try:
            selected_year, selected_month = map(int, month_year.split('-'))
            registrations = registrations.filter(
                shift_instance__work_date__year=selected_year,
                shift_instance__work_date__month=selected_month
            )
        except ValueError:
            pass

    if selected_year and selected_month and week:
        try:
            week_num = int(week)
            month_matrix = calendar.monthcalendar(selected_year, selected_month)

            if 1 <= week_num <= len(month_matrix):
                valid_days = [d for d in month_matrix[week_num - 1] if d != 0]

                selected_week_dates = [
                    date(selected_year, selected_month, d)
                    for d in valid_days
                ]

                registrations = registrations.filter(
                    shift_instance__work_date__day__in=valid_days
                )
        except ValueError:
            pass

    registrations = list(registrations)

    if not registrations:
        return JsonResponse({
            'status': 'error',
            'message': 'Không tìm thấy dữ liệu lịch của nhân viên này.'
        }, status=404)

    employee = registrations[0].employee
    position_name = ''
    if hasattr(employee, 'position') and employee.position:
        position_name = str(employee.position)

    priority = {'PENDING': 3, 'REJECTED': 2, 'APPROVED': 1}
    final_status = 'APPROVED'
    for reg in registrations:
        if priority.get(reg.approval_status, 0) > priority.get(final_status, 0):
            final_status = reg.approval_status

    if final_status == 'APPROVED':
        status_text = 'Duyệt'
    elif final_status == 'PENDING':
        status_text = 'Chờ duyệt'
    else:
        status_text = 'Từ chối'

    detail_items = []
    work_dates_set = set()

    for reg in registrations:
        shift_instance = reg.shift_instance
        shift = shift_instance.shift
        work_date = shift_instance.work_date
        work_dates_set.add(work_date)

        shift_name = getattr(shift, 'shift_name', '')
        start_time = getattr(shift, 'start_time', None)
        end_time = getattr(shift, 'end_time', None)

        if start_time and end_time:
            time_text = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            if shift_name:
                time_text += f" ({shift_name.lower()})"
        else:
            time_text = shift_name if shift_name else 'Ca làm'

        if reg.approval_status == 'APPROVED':
            item_status = 'approved'
        elif reg.approval_status == 'PENDING':
            item_status = 'pending'
        else:
            item_status = 'rejected'

        detail_items.append({
            'date': work_date.strftime('%d'),
            'month': f"T{work_date.month:02d}",
            'weekday': f"T{work_date.isoweekday()}",
            'work_date': work_date.strftime('%d/%m/%Y'),
            'time_text': time_text,
            'position_name': position_name or 'Chưa có vị trí',
            'status': item_status,
        })

    # Nếu có chọn tuần thì thêm các ngày nghỉ chưa đăng ký
    if selected_week_dates:
        existing_dates = {reg.shift_instance.work_date for reg in registrations}

        for d in selected_week_dates:
            if d not in existing_dates:
                detail_items.append({
                    'date': d.strftime('%d'),
                    'month': f"T{d.month:02d}",
                    'weekday': f"T{d.isoweekday()}",
                    'work_date': d.strftime('%d/%m/%Y'),
                    'time_text': 'Nghỉ',
                    'position_name': '',
                    'status': 'off',
                })

        detail_items.sort(key=lambda x: datetime.strptime(x['work_date'], '%d/%m/%Y'))

    response_data = {
        'status': 'success',
        'employee': {
            'employee_id': employee.employee_id,
            'employee_code': f'NV{str(employee.employee_id).zfill(3)}',
            'full_name': employee.full_name,
            'position_name': position_name or 'Chưa có vị trí',
            'initials': ''.join([w[0] for w in employee.full_name.split()[:2]]).upper(),
        },
        'summary': {
            'total_days': len(work_dates_set),
            'total_hours': len(registrations) * 5,
            'status_text': status_text,
        },
        'details': detail_items,
    }

    return JsonResponse(response_data)


def tao_lich_lam_viec(request):
    context = {
        'url_name': 'taolichlamviec',
    }
    return render(request, 'schedule/taolichlamviec.html', context)


def api_capacity(request):
    if request.method == "GET":
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            return JsonResponse({
                'status': 'error',
                'message': 'Thiếu tham số ngày tháng'
            })

        try:
            positions = list(Position.objects.values_list('position_name', flat=True))
            if not positions:
                positions = ['Phục vụ', 'Pha chế', 'Phụ bếp', 'Thu ngân']
        except Exception as e:
            print(f"\n[CẢNH BÁO 1] Lỗi bảng Position: {e}")
            positions = ['Phục vụ', 'Pha chế', 'Phụ bếp', 'Thu ngân']

        ca_keys = ['sang', 'chieu', 'toi']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        schedule_data = {}
        delta = end_date - start_date

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            schedule_data[day_str] = {ca: {pos: 0 for pos in positions} for ca in ca_keys}

        try:
            capacities = ScheduleCapacity.objects.filter(
                shift_instance__work_date__range=[start_date, end_date]
            ).select_related('shift_instance__shift', 'position')

            for cap in capacities:
                d_str = cap.shift_instance.work_date.strftime('%Y-%m-%d')

                shift_name = cap.shift_instance.shift.shift_name.strip().lower()

                if 'sáng' in shift_name or 'sang' in shift_name:
                    ca = 'sang'
                elif 'chiều' in shift_name or 'chieu' in shift_name:
                    ca = 'chieu'
                elif 'tối' in shift_name or 'toi' in shift_name:
                    ca = 'toi'
                else:
                    continue

                pos_name = cap.position.position_name

                if d_str in schedule_data and ca in schedule_data[d_str] and pos_name in schedule_data[d_str][ca]:
                    schedule_data[d_str][ca][pos_name] = cap.max_quantity

        except Exception as e:
            print(f"\n[CẢNH BÁO 2] Lỗi khi đọc ScheduleCapacity: {e}")

        return JsonResponse({
            'status': 'success',
            'data': schedule_data
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            schedule = data.get('schedule', {})

            for date_str, shifts in schedule.items():
                work_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                for shift_type, positions_dict in shifts.items():

                    if shift_type == 'sang':
                        shift_obj = Shift.objects.get(shift_name__icontains='Sáng')
                    elif shift_type == 'chieu':
                        shift_obj = Shift.objects.get(shift_name__icontains='Chiều')
                    elif shift_type == 'toi':
                        shift_obj = Shift.objects.get(shift_name__icontains='Tối')
                    else:
                        continue

                    shift_inst, _ = ShiftInstance.objects.get_or_create(
                        work_date=work_date,
                        shift=shift_obj
                    )

                    for pos_name, qty in positions_dict.items():
                        pos = Position.objects.get(position_name=pos_name)

                        ScheduleCapacity.objects.update_or_create(
                            position=pos,
                            shift_instance=shift_inst,
                            defaults={'max_quantity': int(qty)}
                        )

            return JsonResponse({
                'status': 'success',
                'message': 'Đã lưu lịch thành công!'
            })

        except Exception as e:
            print(f"\n[CẢNH BÁO LỖI LƯU DATA] Lỗi chi tiết: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi backend: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Method không hợp lệ'
    }, status=405)


def xoa_lich_lam_viec(request):
    context = {
        'url_name': 'xoalichlamviec',
    }
    return render(request, 'schedule/xoalichlamviec.html', context)

@require_GET
def api_delete_schedule_weeks(request):
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    week_value = request.GET.get('week', '').strip()

    registrations = ScheduleRegistration.objects.select_related(
        'employee',
        'shift_instance'
    ).all().order_by('shift_instance__work_date')

    # lọc theo ngày
    if from_date:
        registrations = registrations.filter(shift_instance__work_date__gte=from_date)
    if to_date:
        registrations = registrations.filter(shift_instance__work_date__lte=to_date)

    # nếu chọn input week
    if week_value:
        try:
            year, week_num = week_value.split('-W')
            year = int(year)
            week_num = int(week_num)
            start_date = datetime.strptime(f'{year}-W{week_num}-1', "%G-W%V-%u").date()
            end_date = start_date + timedelta(days=6)

            registrations = registrations.filter(
                shift_instance__work_date__range=[start_date, end_date]
            )
        except Exception:
            return JsonResponse({
                'status': 'error',
                'message': 'Tuần không hợp lệ'
            }, status=400)

    regs = list(registrations)

    week_map = {}
    for reg in regs:
        work_date = reg.shift_instance.work_date
        iso_year, iso_week, _ = work_date.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"

        monday = work_date - timedelta(days=work_date.weekday())
        sunday = monday + timedelta(days=6)

        if key not in week_map:
            week_map[key] = {
                'week_key': key,
                'label': f"Tuần {iso_week}",
                'from': monday.strftime('%Y-%m-%d'),
                'to': sunday.strftime('%Y-%m-%d'),
                'range': f"{monday.strftime('%d/%m/%Y')} - {sunday.strftime('%d/%m/%Y')}",
                'employee_ids': set(),
                'shift_count': 0,
                'monday': monday,
                'status': 'upcoming'
            }

        week_map[key]['employee_ids'].add(reg.employee.employee_id)
        week_map[key]['shift_count'] += 1

    weeks_sorted = sorted(week_map.values(), key=lambda x: x['monday'])

    weeks = []
    for idx, item in enumerate(weeks_sorted, start=1):
        weeks.append({
            'id': idx,  # rất quan trọng: id tuần frontend dùng để gọi detail
            'week_key': item['week_key'],
            'label': item['label'],
            'from': item['from'],
            'to': item['to'],
            'range': item['range'],
            'employees': len(item['employee_ids']),
            'shifts': item['shift_count'],
            'status': item['status'],
        })

    return JsonResponse({
        'status': 'success',
        'weeks': weeks
    })
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime, timedelta

@require_GET
def api_delete_schedule_week_detail(request, week_id):
    search_name = request.GET.get('name', '').strip().lower()

    # week_id ở đây là id đơn giản: 1, 2, 3...
    # nên ta phải tìm lại từ API tuần / hoặc map trực tiếp theo dữ liệu đăng ký
    # Cách ổn định nhất: lấy tất cả registration, gom theo tuần, rồi chọn tuần thứ N theo thứ tự

    registrations = ScheduleRegistration.objects.select_related(
        'employee',
        'shift_instance',
        'shift_instance__shift'
    ).all().order_by('shift_instance__work_date')

    # Gom dữ liệu theo tuần ISO
    week_map = {}
    for reg in registrations:
        work_date = reg.shift_instance.work_date
        iso_year, iso_week, _ = work_date.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"

        monday = work_date - timedelta(days=work_date.weekday())
        sunday = monday + timedelta(days=6)

        if key not in week_map:
            week_map[key] = {
                'week_key': key,
                'label': f"Tuần {iso_week}",
                'range': f"{monday.strftime('%d/%m/%Y')} - {sunday.strftime('%d/%m/%Y')}",
                'monday': monday,
                'sunday': sunday,
                'registrations': []
            }

        week_map[key]['registrations'].append(reg)

    weeks_sorted = sorted(
        week_map.values(),
        key=lambda x: x['monday']
    )

    # week_id frontend đang gửi 1,2,3... => map theo thứ tự card
    if week_id < 1 or week_id > len(weeks_sorted):
        return JsonResponse({
            'status': 'error',
            'message': 'Không tìm thấy tuần'
        }, status=404)

    selected_week = weeks_sorted[week_id - 1]
    monday = selected_week['monday']
    regs = selected_week['registrations']

    employee_map = {}

    for reg in regs:
        emp = reg.employee

        if search_name and search_name not in emp.full_name.lower():
            continue

        emp_id = str(emp.employee_id)

        if emp_id not in employee_map:
            avatar = ''.join([w[0] for w in emp.full_name.split()[:2]]).upper()

            employee_map[emp_id] = {
                'id': emp_id,
                'code': f"NV{str(emp.employee_id).zfill(3)}",
                'name': emp.full_name,
                'role': str(emp.position) if hasattr(emp, 'position') and emp.position else 'Chưa có vị trí',
                'avatar': avatar,
                'days': ['' for _ in range(7)],
            }

        idx = (reg.shift_instance.work_date - monday).days
        if 0 <= idx <= 6:
            shift_name = reg.shift_instance.shift.shift_name if reg.shift_instance and reg.shift_instance.shift else 'Ca làm'
            employee_map[emp_id]['days'][idx] = shift_name

    employees_data = list(employee_map.values())

    return JsonResponse({
        'status': 'success',
        'week': {
            'id': week_id,
            'week_key': selected_week['week_key'],
            'label': selected_week['label'],
            'range': selected_week['range'],
        },
        'employees_data': employees_data
    })
@require_http_methods(["POST"])
def api_delete_schedule_delete(request):
    try:
        data = json.loads(request.body)
        delete_type = data.get('type')
        employee_id = data.get('employee_id')
        week_key = data.get('week_key')
        selected_days = data.get('selected_days', [])

        if not employee_id or not week_key:
            return JsonResponse({
                'status': 'error',
                'message': 'Thiếu employee_id hoặc week_key'
            }, status=400)

        year_str, week_str = week_key.split('-W')
        year = int(year_str)
        iso_week = int(week_str)
        week_start = date.fromisocalendar(year, iso_week, 1)
        week_end = date.fromisocalendar(year, iso_week, 7)

        qs = ScheduleRegistration.objects.filter(
            employee__employee_id=employee_id,
            shift_instance__work_date__range=[week_start, week_end]
        )

        if delete_type == 'employee':
            deleted_count, _ = qs.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Đã xóa toàn bộ lịch tuần của nhân viên.',
                'deleted_count': deleted_count
            })

        elif delete_type == 'days':
            if not selected_days:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Chưa chọn ngày để xóa'
                }, status=400)

            selected_dates = []
            for day_index in selected_days:
                d = week_start + timedelta(days=int(day_index))
                selected_dates.append(d)

            deleted_count, _ = qs.filter(
                shift_instance__work_date__in=selected_dates
            ).delete()

            return JsonResponse({
                'status': 'success',
                'message': 'Đã xóa các ngày đã chọn.',
                'deleted_count': deleted_count
            })

        return JsonResponse({
            'status': 'error',
            'message': 'type không hợp lệ'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi backend: {str(e)}'
        }, status=500)

def duyet_lich_lam_viec(request):
    context = {
        'url_name': 'duyetlichlam',
    }
    return render(request, 'schedule/duyetlichlamviec.html', context)

@require_GET
def api_approve_schedule_list(request):
    name = request.GET.get('name', '').strip()
    month_year = request.GET.get('month_year', '').strip()
    week = request.GET.get('week', '').strip()
    shift_type = request.GET.get('shift_type', '').strip()

    registrations = ScheduleRegistration.objects.select_related(
        'employee',
        'shift_instance',
        'shift_instance__shift'
    ).all().order_by('-registration_date')

    # lọc theo tên
    if name:
        registrations = registrations.filter(employee__full_name__icontains=name)

    selected_year = None
    selected_month = None

    # lọc theo tháng/năm
    if month_year:
        try:
            selected_month, selected_year = month_year.split('-')
            selected_month = int(selected_month)
            selected_year = int(selected_year)

            registrations = registrations.filter(
                shift_instance__work_date__year=selected_year,
                shift_instance__work_date__month=selected_month
            )
        except Exception:
            pass

    # lọc theo tuần trong tháng
    if selected_year and selected_month and week:
        try:
            week_num = int(week)
            month_matrix = calendar.monthcalendar(selected_year, selected_month)

            if 1 <= week_num <= len(month_matrix):
                valid_days = [d for d in month_matrix[week_num - 1] if d != 0]
                registrations = registrations.filter(
                    shift_instance__work_date__day__in=valid_days
                )
        except Exception:
            pass

    # lọc theo ca làm
    if shift_type:
        if shift_type == 'sang':
            registrations = registrations.filter(shift_instance__shift__shift_name__icontains='Sáng')
        elif shift_type == 'chieu':
            registrations = registrations.filter(shift_instance__shift__shift_name__icontains='Chiều')
        elif shift_type == 'toi':
            registrations = registrations.filter(shift_instance__shift__shift_name__icontains='Tối')

    # gom theo nhân viên
    employee_map = {}

    for reg in registrations:
        emp = reg.employee
        emp_id = emp.employee_id

        if emp_id not in employee_map:
            employee_map[emp_id] = {
                'id': emp_id,
                'code': f"NV{str(emp.employee_id).zfill(3)}",
                'name': emp.full_name,
                'days_set': set(),
                'hours': 0,
                'reg_time': reg.registration_date,
                'status': reg.approval_status,
            }

        employee_map[emp_id]['days_set'].add(reg.shift_instance.work_date)
        employee_map[emp_id]['hours'] += 5

        if reg.registration_date > employee_map[emp_id]['reg_time']:
            employee_map[emp_id]['reg_time'] = reg.registration_date

        # ưu tiên trạng thái
        priority = {'PENDING': 3, 'REJECTED': 2, 'APPROVED': 1}
        old_status = employee_map[emp_id]['status']
        new_status = reg.approval_status
        if priority.get(new_status, 0) > priority.get(old_status, 0):
            employee_map[emp_id]['status'] = new_status

    rows = []
    for emp_data in employee_map.values():
        status = emp_data['status']
        if status == 'APPROVED':
            status_text = 'Đã duyệt'
            status_class = 'approved'
        elif status == 'REJECTED':
            status_text = 'Từ chối'
            status_class = 'rejected'
        else:
            status_text = 'Đang chờ'
            status_class = 'pending'

        rows.append({
            'id': emp_data['id'],
            'code': emp_data['code'],
            'name': emp_data['name'],
            'days': len(emp_data['days_set']),
            'hours': emp_data['hours'],
            'reg_time': emp_data['reg_time'].strftime('%d/%m/%Y %H:%M'),
            'status': status,
            'status_text': status_text,
            'status_class': status_class,
        })

    rows.sort(key=lambda x: x['code'])

    approved_count = len([r for r in rows if r['status'] == 'APPROVED'])
    pending_count = len([r for r in rows if r['status'] == 'PENDING'])
    rejected_count = len([r for r in rows if r['status'] == 'REJECTED'])

    return JsonResponse({
        'status': 'success',
        'rows': rows,
        'stats': {
            'total': len(rows),
            'approved': approved_count,
            'pending': pending_count,
            'rejected': rejected_count,
        }
    })
@require_POST
def api_approve_schedule_update(request):
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        action = data.get('action')

        if not employee_id or action not in ['approve', 'reject']:
            return JsonResponse({
                'status': 'error',
                'message': 'Thiếu dữ liệu đầu vào'
            }, status=400)

        qs = ScheduleRegistration.objects.filter(
            employee__employee_id=employee_id,
            approval_status='PENDING'
        )

        if not qs.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Không có lịch chờ duyệt của nhân viên này'
            }, status=404)

        new_status = 'APPROVED' if action == 'approve' else 'REJECTED'
        qs.update(approval_status=new_status)

        return JsonResponse({
            'status': 'success',
            'message': 'Cập nhật trạng thái thành công'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi backend: {str(e)}'
        }, status=500)