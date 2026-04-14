from django.db import models
from django.contrib.auth.models import User, Group

class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    position_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.position_name

class SalaryLevel(models.Model):
    salary_level_id = models.AutoField(primary_key=True)
    level_name = models.CharField(max_length=100) # Vd: Pha chế thử việc, Pha chế chính thức
    base_salary = models.FloatField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.level_name} - {self.base_salary:,.0f}đ"

class Employee(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    hire_date = models.DateField()
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    citizen_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name

class PositionDetail(models.Model):
    STATUS_CHOICES = (
        ('probation', 'Thử việc'),
        ('official', 'Chính thức')
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    applied_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='probation')

    class Meta:
        unique_together = ('employee', 'position')

class SalaryDetail(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary_level = models.ForeignKey(SalaryLevel, on_delete=models.CASCADE)
    applied_date = models.DateField()

    class Meta:
        unique_together = ('employee', 'salary_level')