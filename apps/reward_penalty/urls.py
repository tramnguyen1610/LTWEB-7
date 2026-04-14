from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.reward_penalty_list, name='reward_penalty_list'),
]