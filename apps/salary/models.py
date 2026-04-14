from django.db import models
from django.db.models import Sum
from decimal import Decimal

from .logic import calculate_payroll_data
PAY_TYPE_CHOICES = (
    ('HOURLY', 'Hourly Wage'),
    ('MONTHLY', 'Fixed Monthly Salary')
)

STATUS_CHOICES = (
    ('probation', 'Probation'),
    ('official', 'Official')
)

class SalaryLevel(models.Model):
    salary_level_id = models.AutoField(primary_key=True)
    level_name = models.CharField(max_length=100, verbose_name="Level Name")
    pay_type = models.CharField(
        max_length=10,
        choices=PAY_TYPE_CHOICES,
        default='HOURLY',
        verbose_name="Pay Type"
    )
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Base Salary"
    )
    position = models.ForeignKey(
        'employees.Position',
        on_delete=models.CASCADE,
        verbose_name="Position"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='probation',
        verbose_name="Status"
    )

    def __str__(self):
        unit = "month" if self.pay_type == 'MONTHLY' else "hour"
        return f"{self.level_name} ({self.base_salary:,.0f} / {unit})"

    class Meta:
        verbose_name = "Salary Level"
        verbose_name_plural = "Salary Levels"


class Payroll(models.Model):
    payroll_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, verbose_name="Nhân viên")
    payroll_period = models.CharField(max_length=7, verbose_name="Kỳ lương (MM-YYYY)")

    total_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Lương cơ bản")
    total_bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng thưởng")
    total_penalty = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng phạt")
    net_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Thực nhận")

    def save(self, *args, **kwargs):
        # 1. Gọi bộ não từ logic.py để lấy số liệu
        calculated_data = calculate_payroll_data(self.employee, self.payroll_period)

        # 2. Gắn số liệu vào Object
        self.total_salary = calculated_data['total_salary']
        self.total_bonus = calculated_data['total_bonus']
        self.total_penalty = calculated_data['total_penalty']

        # 3. Tính Thực nhận
        self.net_salary = self.total_salary + self.total_bonus - self.total_penalty

        # 4. Lưu xuống Database
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Lương {self.employee.full_name} - {self.payroll_period}"