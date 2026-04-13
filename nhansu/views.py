# views.py (cùng cấp với manage.py)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employees.models import Employee


def login_view(request):
    if request.user.is_authenticated:
        # Nếu đã login thì chuyển sang dashboard tương ứng
        try:
            employee = request.user.employee
            return redirect('dashboard_nv')
        except:
            return redirect('dashboard_admin')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Kiểm tra role: có employee hay không
            try:
                employee = user.employee
                return redirect('dashboard_nv')
            except:
                return redirect('dashboard_admin')
        else:
            return render(request, 'auth/auth.html', {'error': 'Sai tài khoản hoặc mật khẩu'})

    return render(request, 'auth/auth.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_admin(request):
    # Nếu là nhân viên thì chuyển sang dashboard nhân viên
    try:
        employee = request.user.employee
        return redirect('dashboard_nv')
    except:
        pass

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    inactive_employees = total_employees - active_employees

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def dashboard_nv(request):
    try:
        employee = request.user.employee
    except:
        return redirect('dashboard_admin')

    context = {
        'employee': employee,
    }
    return render(request, 'dashboard/nv_dashboard.html', context)