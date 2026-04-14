from django.contrib import admin
from .models import Position, Employee

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'position_name', 'group')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'position', 'status', 'salary_level')
    list_filter = ('position', 'status')
    search_fields = ('full_name', 'citizen_id', 'phone_number')