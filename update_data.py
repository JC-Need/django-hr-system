import os
import django
import datetime

# 1. ตั้งค่าระบบให้รู้จัก Django (เหมือนเราไขกุญแจเข้าออฟฟิศ)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycompany.settings')
django.setup()

from employees.models import Employee

# 2. เริ่มภารกิจจัดระเบียบ
print("🚀 กำลังเริ่มจัดระเบียบพนักงาน...")

all_emps = Employee.objects.all()
count = 1

for emp in all_emps:
    # A. สร้างรหัสพนักงาน (ถ้ายังไม่มี)
    if not emp.emp_id:
        emp.emp_id = f"STF-{count:03d}"
        count += 1
    
    # B. เดาแผนกจากชื่อ/ตำแหน่ง (ถ้ายังไม่มี)
    if not emp.department:
        if "Dev" in emp.name or "Dev" in emp.position:
            emp.department = "Information Tech"
        elif "Sales" in emp.name or "Sales" in emp.position:
            emp.department = "Sales"
        elif "Ops" in emp.name:
            emp.department = "Operations"
        elif "CEO" in emp.position or "Director" in emp.position:
            emp.department = "Management"
        else:
            emp.department = "General Admin"

    # C. เติมวันเกิดและวันเริ่มงาน (ถ้ายังว่าง)
    if not emp.birth_date:
        emp.birth_date = datetime.date(1995, 1, 1)
    if not emp.hire_date:
        emp.hire_date = datetime.date(2023, 1, 1)
        
    # D. ปรับสถานะให้เป็น ACTIVE ทั้งหมด
    emp.status = 'ACTIVE'

    # บันทึก
    emp.save()
    print(f"✅ อัปเดต: {emp.name} -> {emp.emp_id} | {emp.department}")

print("\n🎉 ภารกิจเสร็จสมบูรณ์! ข้อมูลครบทุกช่องแล้วครับบอส!")