from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Position Name")
    base_salary = models.FloatField(default=0, verbose_name="Base Salary/Hour")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"


# Bảng Nhân viên
class Employee(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))

    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, verbose_name="Position")
    full_name = models.CharField(max_length=255, verbose_name='Full Name')
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Gender')
    phone_number = models.CharField(max_length=15, verbose_name='Phone Number')
    hire_date = models.DateField(verbose_name='Hire Date')

    # Các trường mở rộng (Đã cho phép để trống để không bị lỗi NOT NULL)
    citizen_id = models.CharField(max_length=20, unique=True, verbose_name='Citizen ID', null=True, blank=True)
    bank_name = models.CharField(max_length=100, verbose_name='Bank Name', blank=True, null=True)
    bank_account = models.CharField(max_length=50, verbose_name='Bank Account', blank=True, null=True)

    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'