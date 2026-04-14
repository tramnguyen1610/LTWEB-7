from django.contrib import admin
from .models import Position, SalaryLevel, Employee, PositionDetail, SalaryDetail

# Để hiện bảng Vị trí ngay trong trang Nhân viên
class PositionDetailInline(admin.TabularInline):
    model = PositionDetail
    extra = 1

# Để hiện bảng Bậc lương ngay trong trang Nhân viên
class SalaryDetailInline(admin.TabularInline):
    model = SalaryDetail
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'phone_number', 'hire_date')
    search_fields = ('full_name', 'citizen_id')
    # Gộp 2 cái Inline vào đây
    inlines = [PositionDetailInline, SalaryDetailInline]

@admin.register(SalaryLevel)
class SalaryLevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'position', 'base_salary')
    list_filter = ('position',)

admin.site.register(Position)