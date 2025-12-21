from django.contrib import admin
from django.urls import path
# บรรทัดนี้สำคัญ: ต้องนำเข้าฟังก์ชัน delete_employee มาด้วย
from employees.views import dashboard, delete_employee 

urlpatterns = [
    # 1. ทางเข้าหน้า Admin
    path('admin/', admin.site.urls),

    # 2. ทางเข้าหน้าหลัก (Dashboard)
    path('', dashboard),

    # 3. ทางเข้าสำหรับสั่งลบ (รับรหัสพนักงานเป็นตัวเลข)
    # เช่น ถ้าเข้า /delete/1/ แปลว่าลบคนรหัส 1
    path('delete/<int:emp_id>/', delete_employee),
]