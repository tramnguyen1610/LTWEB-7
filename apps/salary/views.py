
from decimal import Decimal
def tinh_luong_thanh_toan(employee, hours_worked):
    """
    Hàm này tự động tính lương dựa trên loại lương của Nhân viên
    """
    salary_lv = employee.salary_level
    if not salary_lv:
        return Decimal('0')

    # Nếu là Lương Cứng (Quản lý)
    if salary_lv.pay_type == 'MONTHLY':
        total_basic = salary_lv.base_salary

    # Nếu là Lương theo giờ (Nhân viên)
    else:
        total_basic = salary_lv.base_salary * Decimal(str(hours_worked))

    return total_basic