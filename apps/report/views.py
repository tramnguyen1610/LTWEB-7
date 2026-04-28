from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, date
from calendar import monthrange
from decimal import Decimal

from apps.employees.models import Employee, Position
from apps.attendance.models import Attendance
from apps.reward_penalty.models import RewardPenalty
from apps.salary.models import Payroll, SalaryLevel


def report_view(request):
    # Lấy tháng/năm từ request
    month = request.GET.get('month')
    year = request.GET.get('year')
    position_id = request.GET.get('position')

    if month and year:
        month = int(month)
        year = int(year)
    else:
        now = timezone.now()
        year = now.year
        month = now.month

    # Lấy danh sách vị trí cho dropdown
    positions = Position.objects.all()

    # Lọc nhân viên theo vị trí
    employees = Employee.objects.all()
    if position_id and position_id != 'all':
        employees = employees.filter(position_id=position_id)

    # Tính số ngày trong tháng
    days_in_month = monthrange(year, month)[1]
    total_employees = employees.count()

    # ========== THỐNG KÊ TỔNG QUAN ==========

    # Tổng số ca chấm công trong tháng
    total_attendance = Attendance.objects.filter(
        attendance_date__year=year,
        attendance_date__month=month,
        employee__in=employees
    ).count()

    # Tỉ lệ chuyên cần
    attendance_rate = round((total_attendance / (total_employees * days_in_month)) * 100,
                            1) if total_employees > 0 else 0

    # Số lượt đi trễ
    total_late = Attendance.objects.filter(
        attendance_date__year=year,
        attendance_date__month=month,
        employee__in=employees,
        late_hours__gt=0
    ).count()

    # Tổng lương thực nhận
    payroll_period = f"{month:02d}-{year}"
    total_salary = Payroll.objects.filter(
        payroll_period=payroll_period,
        employee__in=employees
    ).aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    # ========== SO SÁNH VỚI THÁNG TRƯỚC ==========

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_days = monthrange(prev_year, prev_month)[1]

    prev_total_employees = Employee.objects.filter(
        hire_date__lte=date(prev_year, prev_month, prev_days)
    ).count()

    prev_attendance = Attendance.objects.filter(
        attendance_date__year=prev_year,
        attendance_date__month=prev_month,
        employee__in=employees
    ).count()
    prev_attendance_rate = round((prev_attendance / (prev_total_employees * prev_days)) * 100,
                                 2) if prev_total_employees > 0 else 0

    prev_late = Attendance.objects.filter(
        attendance_date__year=prev_year,
        attendance_date__month=prev_month,
        employee__in=employees,
        late_hours__gt=0
    ).count()

    prev_salary = Payroll.objects.filter(
        payroll_period=f"{prev_month:02d}-{prev_year}",
        employee__in=employees
    ).aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    # Tính thay đổi
    emp_change = total_employees - prev_total_employees
    rate_change = round(attendance_rate - prev_attendance_rate, 1)
    late_change = total_late - prev_late
    salary_change = float(total_salary - prev_salary)

    # ========== BẢNG CHI TIẾT NHÂN VIÊN ==========

    employee_reports = []
    for emp in employees:
        # Số ngày công
        work_days = Attendance.objects.filter(
            employee=emp,
            attendance_date__year=year,
            attendance_date__month=month
        ).count()

        # Số ngày nghỉ
        off_days = days_in_month - work_days

        # Số lần đi trễ
        late_count = Attendance.objects.filter(
            employee=emp,
            attendance_date__year=year,
            attendance_date__month=month,
            late_hours__gt=0
        ).count()

        # Thưởng trong tháng
        bonus = RewardPenalty.objects.filter(
            employee=emp,
            type='reward',
            date_applied__year=year,
            date_applied__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Phạt trong tháng
        penalty = RewardPenalty.objects.filter(
            employee=emp,
            type='penalty',
            date_applied__year=year,
            date_applied__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Lấy lương thực nhận
        payroll = Payroll.objects.filter(
            employee=emp,
            payroll_period=payroll_period
        ).first()
        net_salary = payroll.net_salary if payroll else 0

        # Xác định trạng thái
        # Xác định trạng thái
        if work_days == days_in_month:
            status = 'Đủ công'
            status_class = 'chip-green'
        elif work_days >= days_in_month - 2:
            status = 'Đủ công'
            status_class = 'chip-green'
        elif work_days >= days_in_month - 5:
            status = 'Thiếu công'
            status_class = 'chip-orange'
        else:
            status = 'Thiếu công nhiều'
            status_class = 'chip-red'

        employee_reports.append({
            'employee_id': f"NV{emp.employee_id:03d}",
            'full_name': emp.full_name,
            'position': emp.position.position_name if emp.position else 'Chưa xác định',
            'work_days': f"{work_days}/{days_in_month}",
            'late_count': late_count,
            'off_days': off_days,
            'bonus': float(bonus),
            'penalty': float(penalty),
            'net_salary': float(net_salary),
            'status': status,
            'status_class': status_class,
        })

    # Sắp xếp theo mã nhân viên
    employee_reports.sort(key=lambda x: x['employee_id'])

    # ========== THỐNG KÊ THƯỞNG PHẠT THEO LÝ DO ==========

    bonus_stats = RewardPenalty.objects.filter(
        type='reward',
        date_applied__year=year,
        date_applied__month=month
    ).values('reason').annotate(total=Sum('amount')).order_by('-total')

    penalty_stats = RewardPenalty.objects.filter(
        type='penalty',
        date_applied__year=year,
        date_applied__month=month
    ).values('reason').annotate(total=Sum('amount')).order_by('-total')

    total_bonus = RewardPenalty.objects.filter(
        type='reward',
        date_applied__year=year,
        date_applied__month=month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_penalty = RewardPenalty.objects.filter(
        type='penalty',
        date_applied__year=year,
        date_applied__month=month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # ========== TOP NHÂN VIÊN XUẤT SẮC ==========

    top_employees = Payroll.objects.filter(
        payroll_period=payroll_period,
        employee__in=employees
    ).select_related('employee').order_by('-net_salary')[:5]

    top_list = []
    for idx, p in enumerate(top_employees, 1):
        top_list.append({
            'rank': idx,
            'name': p.employee.full_name,
            'position': p.employee.position.position_name if p.employee.position else 'Nhân viên',
            'salary': float(p.net_salary),
        })

    # ========== THỐNG KÊ THEO VỊ TRÍ ==========

    position_stats = []
    for pos in positions:
        emp_count = employees.filter(position=pos).count()
        if emp_count > 0:
            pos_payroll = Payroll.objects.filter(
                payroll_period=payroll_period,
                employee__position=pos,
                employee__in=employees
            ).aggregate(Sum('net_salary'))['net_salary__sum'] or 0

            position_stats.append({
                'name': pos.position_name,
                'count': emp_count,
                'total_salary': float(pos_payroll),
                'avg_salary': float(pos_payroll / emp_count) if emp_count > 0 else 0,
            })

    context = {
        # Thông tin tháng
        'month': month,
        'year': year,
        'month_name': f"Tháng {month}/{year}",
        'selected_month': f"{year}-{month:02d}",
        'positions': positions,
        'selected_position': position_id,

        # Thống kê tổng quan
        'total_employees': total_employees,
        'total_employees_change': emp_change,
        'attendance_rate': attendance_rate,
        'attendance_rate_change': rate_change,
        'total_late': total_late,
        'total_late_change': late_change,
        'total_salary': float(total_salary),
        'total_salary_change': salary_change,

        # Thống kê chi tiết
        'full_count': len([e for e in employee_reports if e['status'] == 'Đủ công']),
        'late_count': len([e for e in employee_reports if e['status'] == 'Thiếu công']),
        'no_permit_count': len([e for e in employee_reports if e['status'] == 'Nghỉ không phép']),

        # Bảng chi tiết
        'employee_reports': employee_reports,

        # Thưởng phạt
        'bonus_stats': list(bonus_stats),
        'penalty_stats': list(penalty_stats),
        'total_bonus': float(total_bonus),
        'total_penalty': float(total_penalty),

        # Top nhân viên
        'top_employees': top_list,

        # Thống kê theo vị trí
        'position_stats': position_stats,
    }

    return render(request, 'report/report.html', context)