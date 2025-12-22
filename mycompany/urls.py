from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views # ดึงระบบล็อกอินมาตรฐานมาใช้
from employees import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- 🔐 โซนระบบสมาชิก (Login/Logout) ---
    path('login/', auth_views.LoginView.as_view(template_name='employees/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # --- 🏢 โซนทำงาน (Dashboard & Actions) ---
    path('', views.dashboard, name='dashboard'), # หน้าแรกก็ให้เป็น dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('leave_request/', views.leave_request, name='leave_request'),
    
    # ฟังก์ชันเบื้องหลัง
    path('calculate_bonus/', views.calculate_bonus, name='calculate_bonus'),
    path('delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('attendance/<int:emp_id>/', views.attendance_action, name='attendance_action'),
]