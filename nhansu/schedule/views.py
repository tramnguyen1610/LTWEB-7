from django.shortcuts import render

# Create your views here.
# schedule/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def schedule_list(request):
    return render(request, 'lichlam/list.html')

@login_required
def schedule_create(request):
    return render(request, 'lichlam/form.html')

@login_required
def schedule_approve(request, pk):
    return render(request, 'lichlam/approve.html')