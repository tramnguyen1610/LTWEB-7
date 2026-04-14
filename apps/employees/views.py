from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from .models import Employee, Position
from django.contrib.auth.models import User


@login_required
@staff_member_required
def employee_list(request):
    """Danh sách nhân viên có tìm kiếm và lọc"""

    # Lấy các tham số từ request
    search_keyword = request.GET.get('search', '').strip()
    position_id = request.GET.get('position', '')
    status_filter = request.GET.get('status', '')
    gender_filter = request.GET.get('gender', '')

    # Khởi tạo queryset
    employees = Employee.objects.select_related('position', 'user').all()

    # Tìm kiếm theo từ khóa
    if search_keyword:
        employees = employees.filter(
            Q(full_name__icontains=search_keyword) |
            Q(employee_id__icontains=search_keyword) |
            Q(phone_number__icontains=search_keyword) |
            Q(citizen_id__icontains=search_keyword) |
            Q(user__username__icontains=search_keyword)
        )

    # Lọc theo vị trí
    if position_id:
        employees = employees.filter(position_id=position_id)

    # Lọc theo tình trạng
    if status_filter:
        employees = employees.filter(status=status_filter)

    # Lọc theo giới tính
    if gender_filter:
        employees = employees.filter(gender=gender_filter)

    # Sắp xếp
    employees = employees.order_by('employee_id')

    # Lấy danh sách vị trí cho dropdown
    positions = Position.objects.all()

    # Phân trang
    paginator = Paginator(employees, 10)
    page = request.GET.get('page', 1)

    try:
        employees_page = paginator.page(page)
    except PageNotAnInteger:
        employees_page = paginator.page(1)
    except EmptyPage:
        employees_page = paginator.page(paginator.num_pages)

    context = {
        'employees': employees_page,
        'search_keyword': search_keyword,
        'selected_position': position_id,
        'selected_status': status_filter,
        'selected_gender': gender_filter,
        'positions': positions,
        'total_results': employees.count(),
    }

    return render(request, 'employees/list.html', context)


@login_required
@staff_member_required
def employee_search_ajax(request):
    """API tìm kiếm nhân viên realtime (AJAX)"""
    keyword = request.GET.get('q', '').strip()

    if keyword:
        employees = Employee.objects.select_related('position').filter(
            Q(full_name__icontains=keyword) |
            Q(employee_id__icontains=keyword) |
            Q(phone_number__icontains=keyword)
        )[:10]
    else:
        employees = Employee.objects.select_related('position').all()[:10]

    data = []
    for emp in employees:
        data.append({
            'id': f'NV{emp.employee_id:03d}',
            'full_name': emp.full_name,
            'phone_number': emp.phone_number,
            'position': emp.position.position_name,
            'status': emp.status,
            'status_text': 'Chính thức' if emp.status == 'official' else 'Thử việc',
            'url': f'/employees/detail/{emp.employee_id}/'
        })

    return JsonResponse({'success': True, 'data': data, 'total': len(data)})


# Các hàm khác giữ nguyên...
@login_required
@staff_member_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    context = {
        'employee': employee,
        'work_days': 0,
        'work_hours': 0,
        'reward_penalty': '0 VNĐ',
    }
    return render(request, 'employees/detail.html', context)


@login_required
@staff_member_required
def employee_add(request):
    positions = Position.objects.all()

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email', '')
            password = request.POST.get('password')

            if User.objects.filter(username=username).exists():
                messages.error(request, f'Tên đăng nhập "{username}" đã tồn tại!')
                return render(request, 'employees/add.html', {'positions': positions})

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=request.POST.get('full_name', '').split()[0] if request.POST.get('full_name') else '',
                last_name=' '.join(request.POST.get('full_name', '').split()[1:]) if len(
                    request.POST.get('full_name', '').split()) > 1 else ''
            )

            employee = Employee(
                user=user,
                full_name=request.POST.get('full_name'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender'),
                phone_number=request.POST.get('phone_number'),
                hire_date=request.POST.get('hire_date'),
                bank_name=request.POST.get('bank_name', ''),
                bank_account=request.POST.get('bank_account', ''),
                citizen_id=request.POST.get('citizen_id'),
                position_id=request.POST.get('position'),
                status=request.POST.get('status', 'probation'),
            )
            employee.save()

            messages.success(request, f'Thêm nhân viên {employee.full_name} thành công!')
            return redirect('employees:employee_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    return render(request, 'employees/add.html', {'positions': positions})


@login_required
@staff_member_required
def employee_edit(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    positions = Position.objects.all()

    if request.method == 'POST':
        try:
            user = employee.user
            user.email = request.POST.get('email', '')

            # Cập nhật tên (first_name, last_name)
            full_name = request.POST.get('full_name', '')
            name_parts = full_name.split()
            if name_parts:
                user.first_name = name_parts[0]
                user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

            # Cập nhật mật khẩu nếu có
            new_password = request.POST.get('password')
            if new_password:
                user.set_password(new_password)
                user.save()

            # Cập nhật employee
            employee.phone_number = request.POST.get('phone_number')
            employee.bank_account = request.POST.get('bank_account', '')
            employee.bank_name = request.POST.get('bank_name', '')
            employee.position_id = request.POST.get('position')
            employee.status = request.POST.get('status', 'probation')
            employee.save()

            messages.success(request, f'Cập nhật nhân viên {employee.full_name} thành công!')
            return redirect('employees:employee_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    return render(request, 'employees/edit.html', {
        'employee': employee,
        'positions': positions
    })


@login_required
@staff_member_required
def employee_delete(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        employee_name = employee.full_name
        user = employee.user
        try:
            employee.delete()
            user.delete()
            messages.success(request, f'Đã xóa nhân viên {employee_name}!')
            return redirect('employees:employee_list')
        except Exception as e:
            messages.error(request, f'Lỗi khi xóa: {str(e)}')

    return render(request, 'employees/delete_confirm.html', {'employee': employee})


@login_required
@staff_member_required
def employee_delete_api(request, employee_id):
    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, employee_id=employee_id)
            user = employee.user
            employee.delete()
            user.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})