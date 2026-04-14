from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('detail/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('add/', views.employee_add, name='employee_add'),
    path('edit/<int:employee_id>/', views.employee_edit, name='employee_edit'),
    path('delete/<int:employee_id>/', views.employee_delete, name='employee_delete'),
    path('api/delete/<int:employee_id>/', views.employee_delete_api, name='employee_delete_api'),
]