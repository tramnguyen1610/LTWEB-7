from django.contrib import admin
from .models import Position, Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'position', 'citizen_id', 'is_active')
    search_fields = ('full_name', 'citizen_id')
    list_filter = ('position', 'is_active')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_salary')