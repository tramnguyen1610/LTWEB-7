# employees/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def employee_list(request):
    return render(request, 'nhanvien/list.html')

@login_required
def employee_create(request):
    return render(request, 'nhanvien/form.html')

@login_required
def employee_detail(request, pk):
    return render(request, 'nhanvien/detail.html')

@login_required
def employee_update(request, pk):
    return render(request, 'nhanvien/form.html')

@login_required
def employee_delete(request, pk):
    return render(request, 'nhanvien/delete_confirm.html')