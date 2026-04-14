from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.reward_penalty.models import RewardPenalty
from apps.salary.models import Payroll


def report_view(request):
    # 1. Lấy tháng/năm hiện tại hoặc từ bộ lọc (filter)
    filter_month = request.GET.get('month')
    if filter_month:
        year, month = map(int, filter_month.split('-'))
    else:
        now = timezone.now()
        year, month = now.year, now.month

    # 2. Tổng nhân viên
    total_employees = Employee.objects.count()

    # 3. Thống kê chuyên cần (Dựa trên Model Attendance bạn vừa gửi)
    # Tỉ lệ chuyên cần = (Số ca có mặt / Tổng số ca được phân) * 100
    total_shifts_this_month = Attendance.objects.filter(attendance_date__month=month,
                                                        attendance_date__year=year).count()
    present_shifts = Attendance.objects.filter(
        attendance_date__month=month,
        attendance_date__year=year,
        status='Present'
    ).count()

    attendance_rate = (present_shifts / total_shifts_this_month * 100) if total_shifts_this_month > 0 else 0

    # 4. Lượt đi trễ ( late_hours > 0)
    total_late_count = Attendance.objects.filter(
        attendance_date__month=month,
        attendance_date__year=year,
        late_hours__gt=0
    ).count()

    # 5. Tổng lương thực nhận tháng này (Dựa trên Model Payroll)
    payroll_period = f"{month:02d}-{year}"
    total_salary_sum = Payroll.objects.filter(payroll_period=payroll_period).aggregate(Sum('net_salary'))[
                           'net_salary__sum'] or 0

    # 6. Dữ liệu cho bảng chi tiết (Gom thông tin từng nhân viên)
    employee_reports = []
    employees = Employee.objects.all()
    for emp in employees:
        # Tính thưởng/phạt riêng từng người
        rp_data = RewardPenalty.objects.filter(employee=emp, date_applied__month=month, date_applied__year=year)
        emp_reward = rp_data.filter(type='reward').aggregate(Sum('amount'))['amount__sum'] or 0
        emp_penalty = rp_data.filter(type='penalty').aggregate(Sum('amount'))['amount__sum'] or 0

        # Lấy lương thực nhận
        emp_payroll = Payroll.objects.filter(employee=emp, payroll_period=payroll_period).first()

        employee_reports.append({
            'full_name': emp.full_name,
            'attendance_count': Attendance.objects.filter(employee=emp, attendance_date__month=month,
                                                          status='Present').count(),
            'reward': emp_reward,
            'penalty': emp_penalty,
            'net_salary': emp_payroll.net_salary if emp_payroll else 0,
        })

    context = {
        'total_employees': total_employees,
        'attendance_rate': round(attendance_rate, 1),
        'total_late_count': total_late_count,
        'total_salary_sum': total_salary_sum,
        'employee_reports': employee_reports,
        'selected_month': f"{year}-{month:02d}"
    }
    return render(request, 'report/report.html', context)