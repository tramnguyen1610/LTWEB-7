from django.db import models
from apps.employees.models import Employee

class Shift(models.Model):
    shift_id = models.AutoField(primary_key=True)
    shift_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.shift_name

class ShiftInstance(models.Model):
    shift_instance_id = models.AutoField(primary_key=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    work_date = models.DateField()

    def __str__(self):
        return f"{self.shift.shift_name} - {self.work_date}"

class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    work_hours = models.FloatField(default=0)
    late_hours = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='present')

    class Meta:
        unique_together = ('employee', 'shift_instance')