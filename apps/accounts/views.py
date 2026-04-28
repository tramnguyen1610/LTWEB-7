from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from apps.employees.models import Employee # Import thêm model này
from django.db.models import Sum
from apps.reward_penalty.models import RewardPenalty

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

def format_vnd(value):
    return "{:,.0f}".format(value or 0).replace(",", ".")
@login_required
def dashboard_manager(request):
    total_emp = Employee.objects.count()

    reward_data = RewardPenalty.objects.filter(type='reward').aggregate(total=Sum('amount'))
    penalty_data = RewardPenalty.objects.filter(type='penalty').aggregate(total=Sum('amount'))

    total_reward = reward_data['total'] or 0
    total_penalty = penalty_data['total'] or 0

    context = {
        'total_employees': total_emp,
        'total_reward': format_vnd(total_reward),
        'total_penalty': format_vnd(total_penalty),
    }

    return render(request, 'dashboard/dashboard_manager.html', context)
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')