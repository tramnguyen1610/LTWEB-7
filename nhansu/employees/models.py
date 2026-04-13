# employees/models.py
from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )

    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    full_name = models.CharField(max_length=255, verbose_name='Họ tên')
    date_of_birth = models.DateField(verbose_name='Ngày sinh')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Giới tính')
    phone_number = models.CharField(max_length=15, verbose_name='Số điện thoại')
    hire_date = models.DateField(verbose_name='Ngày vào làm')
    bank_name = models.CharField(max_length=100, verbose_name='Ngân hàng', blank=True, null=True)
    bank_account = models.CharField(max_length=50, verbose_name='Số tài khoản', blank=True, null=True)
    citizen_id = models.CharField(max_length=20, unique=True, verbose_name='CMND/CCCD')
    is_active = models.BooleanField(default=True, verbose_name='Đang làm việc')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employee'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'