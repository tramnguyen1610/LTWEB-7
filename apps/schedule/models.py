from django.db import models
from apps.employees.models import Employee, Position
from apps.attendance.models import ShiftInstance

class ScheduleCapacity(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Vị trí")
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE, verbose_name="Phiên làm việc")
    max_quantity = models.PositiveIntegerField(verbose_name="Số lượng tối đa")

    class Meta:
        unique_together = (('position', 'shift_instance'),)

class ScheduleRegistration(models.Model):
    STATUS_CHOICES = [('PENDING', 'Chờ duyệt'), ('APPROVED', 'Đã duyệt'), ('REJECTED', 'Từ chối')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE, verbose_name="Ca đăng ký")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký")
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")

    class Meta:
        unique_together = (('employee', 'shift_instance'),)