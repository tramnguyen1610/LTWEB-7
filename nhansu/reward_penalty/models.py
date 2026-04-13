from django.db import models

# Create your models here.
# reward_penalty/models.py
from django.db import models
from employees.models import Employee


class RewardPenalty(models.Model):
    TYPE_CHOICES = (
        ('bonus', 'Thưởng'),
        ('penalty', 'Phạt'),
    )

    reward_penalty_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reward_penalties')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Loại')
    description = models.TextField(verbose_name='Mô tả')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Số tiền')
    applied_date = models.DateField(verbose_name='Ngày áp dụng')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_type_display()}: {self.amount}"

    class Meta:
        db_table = 'reward_penalty'
        verbose_name = 'Thưởng phạt'
        verbose_name_plural = 'Thưởng phạt'