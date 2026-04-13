# attendance/models.py
from django.db import models
from ..employees.models import Employee


class ShiftInstance(models.Model):
    shift_instance_id = models.AutoField(primary_key=True)
    shift_id = models.IntegerField(verbose_name='ID ca')
    work_date = models.DateField(verbose_name='Ngày làm việc')
    start_time = models.TimeField(verbose_name='Giờ bắt đầu', null=True, blank=True)
    end_time = models.TimeField(verbose_name='Giờ kết thúc', null=True, blank=True)

    def __str__(self):
        return f"Ca {self.shift_id} - {self.work_date}"

    class Meta:
        db_table = 'shift_instance'
        verbose_name = 'Ca làm việc'
        verbose_name_plural = 'Ca làm việc'


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Có mặt'),
        ('absent', 'Vắng mặt'),
        ('late', 'Đi muộn'),
        ('leave', 'Nghỉ phép'),
    )

    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.SET_NULL, null=True, blank=True)
    attendance_date = models.DateField(verbose_name='Ngày chấm công')
    check_in_time = models.TimeField(verbose_name='Giờ vào', null=True, blank=True)
    check_out_time = models.TimeField(verbose_name='Giờ ra', null=True, blank=True)
    work_hours = models.FloatField(default=0, verbose_name='Số giờ làm')
    late_hours = models.FloatField(default=0, verbose_name='Số giờ đi muộn')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_date}"

    class Meta:
        db_table = 'attendance'
        verbose_name = 'Chấm công'
        verbose_name_plural = 'Chấm công'
        unique_together = ['employee', 'attendance_date']