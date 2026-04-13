from django.shortcuts import render

# Create your views here.
# salary/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def salary_list(request):
    return render(request, 'luong/list.html')

@login_required
def salary_calculate(request):
    return render(request, 'luong/calculate.html')

@login_required
def salary_detail(request, pk):
    return render(request, 'luong/detail.html')