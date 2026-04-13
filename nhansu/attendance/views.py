from django.shortcuts import render

# Create your views here.
# attendance/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def attendance_list(request):
    return render(request, 'chamcong/list.html')

@login_required
def attendance_checkin(request):
    return render(request, 'chamcong/checkin.html')

@login_required
def attendance_detail(request, pk):
    return render(request, 'chamcong/detail.html')