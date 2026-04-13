from django.contrib import admin
from .models import Shift, ShiftInstance, Attendance

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_name', 'start_time', 'end_time')

@admin.register(ShiftInstance)
class ShiftInstanceAdmin(admin.ModelAdmin):
    list_display = ('shift_instance_id', 'shift', 'work_date')
    list_filter = ('work_date', 'shift')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift_instance', 'attendance_date', 'status', 'work_hours')
    list_filter = ('status', 'attendance_date')