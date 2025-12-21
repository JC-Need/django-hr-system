from django.contrib import admin
from .models import Employee

# สั่งให้เอาระบบ Employees ไปโชว์หน้า Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'manager', 'level_weight') # เลือกหัวข้อที่จะโชว์ในตาราง
    search_fields = ('name',) # ให้ค้นหาชื่อได้ด้วย