from django.contrib import admin
from .models import SalaryLevel, Employee, SalaryDetail

admin.site.register(SalaryLevel)
admin.site.register(Employee)
admin.site.register(SalaryDetail)