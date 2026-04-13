from django.db import models

# Create your models here.
# schedule/models.py
from django.db import models
from employees.models import Employee
from attendance.models import ShiftInstance


class ScheduleCapacity(models.Model):
    position_id = models.IntegerField(verbose_name='ID vị trí')
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE)
    max_quantity = models.IntegerField(verbose_name='Số lượng tối đa', default=0)

    def __str__(self):
        return f"Vị trí {self.position_id} - Ca {self.shift_instance.shift_id}: {self.max_quantity}"

    class Meta:
        db_table = 'schedule_capacity'
        verbose_name = 'Sức chứa lịch làm'
        verbose_name_plural = 'Sức chứa lịch làm'
        unique_together = ['position_id', 'shift_instance']


class ScheduleRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_instance = models.ForeignKey(ShiftInstance, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.employee.full_name} - {self.shift_instance} - {self.get_approval_status_display()}"

    class Meta:
        db_table = 'schedule_registration'
        verbose_name = 'Đăng ký lịch làm'
        verbose_name_plural = 'Đăng ký lịch làm'
        unique_together = ['employee', 'shift_instance']