from django.contrib import admin
from django.db.models import Sum
from decimal import Decimal
from .models import SalaryLevel, Payroll
from apps.attendance.models import Attendance
from apps.reward_penalty.models import RewardPenalty

# (Giữ nguyên phần đăng ký SalaryLevelAdmin nếu có)
admin.site.register(SalaryLevel)

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll_period', 'total_salary', 'net_salary')

    # Chỉ hiện các trường này trong form
    fields = ('employee', 'payroll_period', 'total_salary', 'total_bonus', 'total_penalty', 'net_salary')

    # KHÓA 4 ô này lại, chỉ cho máy tính điền
    readonly_fields = ('total_salary', 'total_bonus', 'total_penalty', 'net_salary')