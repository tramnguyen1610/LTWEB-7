from django.shortcuts import render

# Create your views here.
# report/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def report_list(request):
    return render(request, 'baocao/list.html')

@login_required
def report_employee(request):
    return render(request, 'baocao/employee.html')

@login_required
def report_salary(request):
    return render(request, 'baocao/salary.html')