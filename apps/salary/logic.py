# apps/salary/logic.py
from django.db.models import Sum
from decimal import Decimal


def calculate_payroll_data(employee, period_str):
    """
    Hàm này nhận vào:
    - employee: Object nhân viên
    - period_str: Chuỗi kỳ lương (Vd: '04-2026')
    Trả về:
    - Một dictionary chứa 3 giá trị: total_salary, total_bonus, total_penalty
    """
    try:
        month, year = map(int, period_str.split('-'))

        # Import trong hàm để tránh lỗi vòng lặp
        from apps.attendance.models import Attendance
        from apps.reward_penalty.models import RewardPenalty

        # 1. Tính tổng giờ làm
        total_hours = Attendance.objects.filter(
            employee=employee,
            attendance_date__month=month,
            attendance_date__year=year
        ).aggregate(Sum('work_hours'))['work_hours__sum'] or 0

        # 2. Tính Thưởng / Phạt
        total_bonus = RewardPenalty.objects.filter(
            employee=employee, type='reward',
            date_applied__month=month, date_applied__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        total_penalty = RewardPenalty.objects.filter(
            employee=employee, type='penalty',
            date_applied__month=month, date_applied__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # 3. Tính Lương cơ bản dựa trên loại lương
        total_salary = Decimal('0')
        salary_lv = employee.salary_level

        if salary_lv:
            if salary_lv.pay_type == 'MONTHLY':
                total_salary = salary_lv.base_salary
            else:
                total_salary = salary_lv.base_salary * Decimal(str(total_hours))

        # Trả về kết quả dưới dạng Từ điển (Dictionary)
        return {
            'total_salary': total_salary,
            'total_bonus': total_bonus,
            'total_penalty': total_penalty
        }

    except Exception as e:
        print(f"Lỗi trong calculate_payroll_data: {e}")
        return {
            'total_salary': Decimal('0'),
            'total_bonus': Decimal('0'),
            'total_penalty': Decimal('0')
        }