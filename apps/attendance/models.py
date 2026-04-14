from django.db import models
from apps.employees.models import Employee

class Shift(models.Model):
    shift_id = models.AutoField(primary_key=True)
    shift_name = models.CharField(max_length=100, verbose_name="Tên ca")
    start_time = models.TimeField(verbose_name="Giờ vào")
    end_time = models.TimeField(verbose_name="Giờ ra")

    def __str__(self):
        return self.shift_name

class ShiftInstance(models.Model):
    shift_instance_id = models.AutoField(primary_key=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Ca làm")
    work_date = models.DateField(verbose_name="Ngày làm")

    def __str__(self):
        return f"{self.shift.shift_name} ({self.work_date})"

class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE, verbose_name="Ca thực tế")
    attendance_date = models.DateField(verbose_name="Ngày chấm công")
    check_in_time = models.TimeField(null=True, blank=True, verbose_name="Giờ vào thực tế")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="Giờ ra thực tế")
    work_hours = models.FloatField(default=0, verbose_name="Số giờ làm")
    late_hours = models.FloatField(default=0, verbose_name="Giờ đi muộn")
    status = models.CharField(max_length=50, default='Present', verbose_name="Trạng thái")

    def __str__(self):
        return f"{self.employee.full_name} - {self.attendance_date}"