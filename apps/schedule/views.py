from django.shortcuts import render, redirect
from .models import ScheduleRegistration
from apps.attendance.models import ShiftInstance

def schedule_register(request):
    if request.method == "POST":
        # Logic đăng ký ca ở đây
        pass
    shifts = ShiftInstance.objects.all()
    return render(request, 'scheduling/register.html', {'shifts': shifts})

def schedule_approve(request):
    registrations = ScheduleRegistration.objects.filter(approval_status='PENDING')
    return render(request, 'scheduling/approve.html', {'registrations': registrations})