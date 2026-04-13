from django.contrib import admin
from .models import Shift, ShiftInstance, Attendance

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')

@admin.register(ShiftInstance)
class ShiftInstanceAdmin(admin.ModelAdmin):
    list_display = ('shift', 'work_date')
    list_filter = ('work_date', 'shift')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift_instance', 'check_in_time', 'check_out_time', 'status')
    list_filter = ('status', 'shift_instance__work_date')
    search_fields = ('employee__full_name',)