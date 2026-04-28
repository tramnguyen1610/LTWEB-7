from django.contrib import admin
from .models import Shift, ShiftInstance, Attendance

admin.site.register(Shift)
admin.site.register(ShiftInstance)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'attendance_date', 'work_hours', 'status')
    list_filter = ('attendance_date', 'status')