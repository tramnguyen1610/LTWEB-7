

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# Hàm redirect tạm thời cho dashboard
def redirect_to_login(request):
    return redirect('/')

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('/employees/'), name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('employees/', include('apps.employees.urls')),
]