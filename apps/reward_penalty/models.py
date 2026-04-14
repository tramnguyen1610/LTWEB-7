from django.db import models
from apps.employees.models import Employee

class RewardPenalty(models.Model):
    # Standardizing choices to English
    TYPE_CHOICES = (
        ('reward', 'Reward'),
        ('penalty', 'Penalty')
    )

    rp_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Employee"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Type"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Amount (VND)"
    )
    reason = models.TextField(verbose_name="Reason")
    date_applied = models.DateField(verbose_name="Date Applied")

    def __str__(self):
        # This will now return "Reward - Tran Thai Thuc Linh"
        return f"{self.get_type_display()} - {self.employee.full_name}"

    class Meta:
        verbose_name = "Reward and Penalty"
        verbose_name_plural = "Rewards and Penalties"