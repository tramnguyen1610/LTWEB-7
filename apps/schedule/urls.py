from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.schedule_register, name='schedule_register'),
    path('approve/', views.schedule_approve, name='schedule_approve'),
]