from django.db import models

# Create your models here.
# report/models.py
from django.db import models


# Nếu không cần lưu báo cáo vào database thì để trống hoặc tạo model tạm
# Chỉ cần file này tồn tại để Django nhận diện app

class Report(models.Model):
    """Model tạm để Django nhận diện app report"""
    name = models.CharField(max_length=100)

    class Meta:
        managed = False  # Không tạo bảng trong database