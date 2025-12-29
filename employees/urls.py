from django.urls import path
from . import views

urlpatterns = [
    # 🏠 1. หน้าแรก (Landing Page)
    path('', views.home, name='home'),

    # 📊 2. หน้า Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 3. หน้าประวัติ & สลิป
    path('employee/<int:emp_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:emp_id>/payslip/', views.employee_payslip, name='employee_payslip'),

    # 4. ระบบลา
    path('leave/create/', views.leave_create, name='leave_create'),
    path('leave/approval/', views.leave_approval, name='leave_approval'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    # 5. โบนัส
    path('bonus/calculate/', views.calculate_bonus, name='calculate_bonus'),

    # 6. ฟังก์ชันเสริม
    path('employee/delete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    path('attendance/<int:emp_id>/', views.attendance_action, name='attendance_action'),

    # 7. หน้ารายละเอียดแผนก
    path('department/<str:dept_name>/', views.department_detail, name='department_detail'),

    # 8. Webhook (LINE Bot)
    path('webhook/', views.line_webhook, name='line_webhook'),

    # 9. จัดการ User & รีเซ็ตรหัสผ่าน
    path('users/manage/', views.user_list, name='user_list'),
    path('users/reset-password/<int:user_id>/', views.admin_reset_password, name='admin_reset_password'),

    # 10. ระบบขายหน้าร้าน (POS System) 🛒 ✅ เพิ่มใหม่ตรงนี้ครับ
    path('pos/', views.pos_home, name='pos_home'),           # หน้าจอขายของ
    path('pos/checkout/', views.pos_checkout, name='pos_checkout'), # ลิงก์สำหรับคิดเงิน

    # 11. ออกจากระบบ
    path('logout/', views.logout_view, name='logout'),
]