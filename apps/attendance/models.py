from django.db import models
from apps.employees.models import Employee


# Bảng Loại Ca Làm (Sáng, Chiều...)
class Shift(models.Model):
    name = models.CharField(max_length=50, verbose_name="Shift Name")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Shift'
        verbose_name_plural = 'Shifts'


# Bảng Lịch Làm Việc (Theo ngày cụ thể)
class ShiftInstance(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Shift Type")
    work_date = models.DateField(verbose_name='Work Date')

    def __str__(self):
        return f"{self.shift.name} - {self.work_date}"

    class Meta:
        verbose_name = 'Shift Instance'
        verbose_name_plural = 'Shift Instances'


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances',
                                 verbose_name="Employee")
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE, verbose_name="Shift Instance")
    check_in_time = models.TimeField(verbose_name='Check-in Time', null=True, blank=True)
    check_out_time = models.TimeField(verbose_name='Check-out Time', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', verbose_name="Status")

    class Meta:
        unique_together = ['employee', 'shift_instance']  # 1 nhân viên chỉ chấm công 1 lần trong 1 ca
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'