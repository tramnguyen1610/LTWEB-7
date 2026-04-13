from django.db import models
from django.contrib.auth.models import User

class SalaryLevel(models.Model):
    salary_level_id = models.AutoField(primary_key=True)
    level_name = models.CharField(max_length=100, verbose_name="Level Name")  # vd: Phục vụ, Pha chế
    base_salary = models.FloatField(verbose_name="Base Salary")

    def __str__(self):
        return self.level_name

class Employee(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    hire_date = models.DateField()
    citizen_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.full_name


class SalaryDetail(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    salary_level = models.ForeignKey(SalaryLevel, on_delete=models.CASCADE)
    applied_date = models.DateField(verbose_name="Applied Date")

    class Meta:
        unique_together = ('employee', 'salary_level')