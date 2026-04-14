from django.shortcuts import render
from .models import RewardPenalty

def reward_penalty_list(request):
    items = RewardPenalty.objects.all().order_by('-date_applied')
    return render(request, 'reward_penalty/lichlam.html', {'items': items})