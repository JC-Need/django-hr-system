from django.urls import path
from . import views

urlpatterns = [
    # 1. หน้า Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alias'),

    # 2. หน้าประวัติ & สลิป
    path('employee/<int:emp_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:emp_id>/payslip/', views.employee_payslip, name='employee_payslip'),

    # 3. ระบบลา
    path('leave/create/', views.leave_create, name='leave_create'),
    path('leave/approval/', views.leave_approval, name='leave_approval'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    # 4. โบนัส
    path('bonus/calculate/', views.calculate_bonus, name='calculate_bonus'),

    # 5. ฟังก์ชันเสริม
    path('employee/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('attendance/<int:emp_id>/', views.attendance_action, name='attendance_action'),
]