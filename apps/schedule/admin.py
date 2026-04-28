from django.contrib import admin
from .models import ScheduleCapacity, ScheduleRegistration

@admin.register(ScheduleCapacity)
class ScheduleCapacityAdmin(admin.ModelAdmin):
    list_display = ('position', 'shift_instance', 'max_quantity')
    list_filter = ('shift_instance__work_date', 'position')

@admin.register(ScheduleRegistration)
class ScheduleRegistrationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift_instance', 'registration_date', 'approval_status')
    list_filter = ('approval_status', 'shift_instance__work_date')
    search_fields = ('employee__full_name',)
    # Thêm action để duyệt nhanh nhiều người cùng lúc
    actions = ['approve_registrations']

    def approve_registrations(self, request, queryset):
        queryset.update(approval_status='APPROVED')
    approve_registrations.short_description = "Duyệt các yêu cầu đã chọn"