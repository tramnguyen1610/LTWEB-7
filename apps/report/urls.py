from django.urls import path
from . import views

urlpatterns = [
    path('hr/', views.hr_report, name='hr_report'),
    path('salary/', views.salary_report, name='salary_report'),
]