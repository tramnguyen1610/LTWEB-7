from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee # Import thêm model này

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard_manager')
        return redirect('dashboard_employee')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('dashboard_manager')
            return redirect('dashboard_employee')

        return render(request, 'auth/auth.html', {
            'error': 'Sai tài khoản hoặc mật khẩu!'
        })

    return render(request, 'auth/auth.html')


@login_required
def dashboard_employee(request):
    if request.user.is_staff:
        return redirect('dashboard_manager')

    # Lấy thông tin chi tiết từ bảng Employee
    try:
        employee = request.user.employee
        display_name = employee.full_name
    except:
        employee = None
        display_name = request.user.username

    context = {
        'employee': employee,
        'display_name': display_name,
        'role_name': 'Nhân viên',
    }
    return render(request, 'dashboard/dashboard_employees.html', context)

@login_required
def dashboard_manager(request):
    if not request.user.is_staff:
        return redirect('dashboard_employee')

    # Tương tự, lấy thông tin Manager từ bảng Employee
    try:
        employee = request.user.employee
        display_name = employee.full_name
    except:
        employee = None
        display_name = request.user.username

    context = {
        'employee': employee,
        'display_name': display_name,
        'role_name': 'Quản lý cửa hàng',
    }
    return render(request, 'dashboard/dashboard_manager.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')