from django.urls import path
from . import views  # Import views cùng thư mục

urlpatterns = [
    path('thiet-lap/', views.reward_penalty_form, name='reward_create'),
    path('xem-thong-tin/', views.reward_penalty_list, name='reward_list'),
]