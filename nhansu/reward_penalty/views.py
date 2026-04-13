from django.shortcuts import render

# Create your views here.
# reward_penalty/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reward_penalty_list(request):
    return render(request, 'thuongphat/list.html')

@login_required
def reward_penalty_create(request):
    return render(request, 'thuongphat/form.html')