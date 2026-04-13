from django.urls import path
from .views import login_view, dashboard_employee, dashboard_manager, logout_view

urlpatterns = [
    path('', login_view, name='login'),
    path('dashboard/nhan-vien/', dashboard_employee, name='dashboard_employee'),
    path('dashboard/quan-ly/', dashboard_manager, name='dashboard_manager'),
    path('logout/', logout_view, name='logout'),
]