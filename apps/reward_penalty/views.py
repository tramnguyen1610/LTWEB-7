from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator  # Thêm phân trang
from .models import RewardPenalty
from apps.employees.models import Employee


def reward_penalty_form(request):
    """Xử lý hiển thị và lưu form thiết lập Thưởng/Phạt"""
    if request.method == "POST":
        # Lấy dữ liệu từ thuộc tính 'name' của các thẻ HTML
        employee_id = request.POST.get('employee')
        rp_type = request.POST.get('type')
        date_applied = request.POST.get('date_applied')
        reason = request.POST.get('reason')
        amount = request.POST.get('amount')

        try:
            # Truy vấn đối tượng nhân viên từ ID
            employee = Employee.objects.get(pk=employee_id)

            # Lưu vào database thông qua Model
            RewardPenalty.objects.create(
                employee=employee,
                type=rp_type,
                amount=amount,
                reason=reason,
                date_applied=date_applied
            )

            # Thông báo thành công và chuyển hướng
            messages.success(request, "Lưu thiết lập thưởng/phạt thành công!")
            return redirect('reward_list')

        except Exception as e:
            messages.error(request, f"Lỗi khi lưu: {str(e)}")

    # Xử lý cho phương thức GET
    employees = Employee.objects.all().order_by('full_name')
    context = {
        'employees': employees,
        'today': timezone.now().date(),
    }
    return render(request, 'reward_penalty/form.html', context)


def reward_penalty_list(request):
    """Xử lý danh sách, tìm kiếm, lọc và thống kê Thưởng/Phạt"""

    # 1. Lấy dữ liệu lọc từ thanh Filter (dựa trên thuộc tính 'name' trong HTML)
    search_name = request.GET.get('q', '')  # Ô tìm kiếm tên
    filter_type = request.GET.get('type', '')  # Dropdown Loại
    filter_month = request.GET.get('month', '')  # Ô chọn tháng

    # 2. Truy vấn gốc (Queryset)
    history_list = RewardPenalty.objects.all().order_by('-date_applied', '-rp_id')

    # 3. Thực hiện lọc dữ liệu linh hoạt
    if search_name:
        history_list = history_list.filter(employee__full_name__icontains=search_name)

    if filter_type:
        history_list = history_list.filter(type=filter_type)

    if filter_month:
        try:
            year, month = filter_month.split('-')
            history_list = history_list.filter(date_applied__year=year, date_applied__month=month)
        except ValueError:
            pass

    # 4. Phân trang (Pagination) - Mỗi trang hiện 10 dòng
    paginator = Paginator(history_list, 10)
    page_number = request.GET.get('page')
    history = paginator.get_page(page_number)

    # 5. Tính toán thống kê (Tính trên dữ liệu thực tế của tháng hiện tại)
    total_employees = Employee.objects.count()
    now = timezone.now()

    reward_data = RewardPenalty.objects.filter(
        type='reward',
        date_applied__month=now.month,
        date_applied__year=now.year
    ).aggregate(Sum('amount'))
    total_reward = reward_data['amount__sum'] or 0

    penalty_data = RewardPenalty.objects.filter(
        type='penalty',
        date_applied__month=now.month,
        date_applied__year=now.year
    ).aggregate(Sum('amount'))
    total_penalty = penalty_data['amount__sum'] or 0

    context = {
        'history': history,
        'total_employees': total_employees,
        'total_reward': total_reward,
        'total_penalty': total_penalty,
    }
    return render(request, 'reward_penalty/list.html', context)