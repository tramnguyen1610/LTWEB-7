from django.contrib import admin
from .models import Shift, ShiftInstance, Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'position', 'shift_instance', 'attendance_date', 'work_hours', 'status')
    list_filter = ('attendance_date', 'status', 'position')
    search_fields = ('employee__full_name',)

@admin.register(ShiftInstance)
class ShiftInstanceAdmin(admin.ModelAdmin):
    list_display = ('shift', 'work_date')
    list_filter = ('work_date',)

admin.site.register(Shift)