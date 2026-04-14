from django.shortcuts import render
from apps.employees.models import Employee
from django.db.models import Count

def hr_report(request):
    # Thống kê nhân viên theo trạng thái (Thử việc/Chính thức)
    stats = Employee.objects.values('status').annotate(total=Count('status'))
    return render(request, 'reports/hr_report.html', {'stats': stats})