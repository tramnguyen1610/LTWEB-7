from django.db import models

# Create your models here.
# salary/models.py
from django.db import models
from ..employees.models import Employee


class SalaryDetail(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_details')
    salary_level_id = models.IntegerField(verbose_name='ID bậc lương')
    level_name = models.CharField(max_length=100, verbose_name='Tên bậc lương')
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Lương cơ bản')
    group_id = models.IntegerField(verbose_name='ID nhóm', default=1)
    effective_date = models.DateField(verbose_name='Ngày hiệu lực', auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.level_name}: {self.base_salary}"

    class Meta:
        db_table = 'salary_detail'
        verbose_name = 'Chi tiết lương'
        verbose_name_plural = 'Chi tiết lương'
        unique_together = ['employee', 'salary_level_id']


class Payroll(models.Model):
    payroll_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    payroll_period = models.CharField(max_length=7, verbose_name='Kỳ lương (MM-YYYY)')
    total_salary = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Tổng lương', default=0)
    total_bonus = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Tổng thưởng')
    total_penalty = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Tổng phạt')
    net_salary = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Lương thực nhận', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period}"

    class Meta:
        db_table = 'payroll'
        verbose_name = 'Bảng lương'
        verbose_name_plural = 'Bảng lương'