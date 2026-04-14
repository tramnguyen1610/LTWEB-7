from django.db import models
from django.contrib.auth.models import User, Group


class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    position_name = models.CharField(max_length=100, verbose_name="Tên vị trí")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.position_name


class Employee(models.Model):
    GENDER_CHOICES = (('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác'))
    STATUS_CHOICES = (
        ('probation', 'Thử việc'),
        ('official', 'Chính thức')
    )

    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, verbose_name="Họ tên")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Giới tính")
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    hire_date = models.DateField(verbose_name="Ngày vào làm")
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ngân hàng")
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name="Số tài khoản")
    citizen_id = models.CharField(max_length=20, unique=True, verbose_name="CCCD")

    # Kết nối trực tiếp để tinh gọn hệ thống
    position = models.ForeignKey(Position, on_delete=models.PROTECT, verbose_name="Vị trí")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='probation', verbose_name="Tình trạng")
    salary_level = models.ForeignKey(
        'salary.SalaryLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Mức lương áp dụng"
    )

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"